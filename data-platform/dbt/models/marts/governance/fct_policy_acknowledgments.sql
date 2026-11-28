-- Who must acknowledge each approved policy, by when, and whether they have.
-- Derived, so the list follows headcount every day: one row per ACTIVE employee (drivers included)
-- per approved policy version in the Policy Register. Owner decision 2026-11-24: all staff
-- acknowledge every approved policy (POL-01 statement 6 names POL-01 and POL-05 as the minimum).
-- Rule (POL-01 statement 6; STD-01 section 11): due 10 business days after the later of the
-- approval date and the hire date. Weekends are skipped; public holidays are not.
-- Announced deadlines (policy_ack_deadlines seed) can only move a due date LATER, never earlier:
-- the 2026-11-25 announcement (blog 459089) set one deadline, 2026-12-09, for POL-01 to POL-15
-- (owner decision 2026-11-27, GOV-107). Staff hired later still get 10 business days from hire.
-- Acknowledgment is per MAJOR version (POL-01 statement 6: each new major version). A minor
-- revision (e.g. POL-07 1.0 -> 1.1) keeps earlier acknowledgments. Limitation: assigned_on uses
-- the register's approval_date, which is the current version's date; if a minor revision is
-- approved on a later date, due dates move with it.
-- Yearly re-acknowledgment (POL-01 statement 6; POL-14 statement 7; GOV-107): an acknowledgment counts
-- for 12 months. next_due_on is 12 months after it; after that the row is 'expired' until the person
-- acknowledges again (a later acknowledgment of the same major version restarts the year). The first
-- yearly cycle falls due in November 2027.
-- DOC-04 (monitoring notice) is included too. Staff acknowledge it by commenting on blog 950312;
-- drivers acknowledge it in the ECT Driver app (simulated).
-- Acknowledgments received: the policy_acknowledgments seed (recorded by hand: approvers and reviewers
-- who acknowledged in their Confluence comments) plus, from 2026-11-28, HR's acknowledgment feed in raw
-- (stg_hris_policy_acknowledgments; simulated by generator 0.5.0). The earliest one counts.
with policies as (
    select doc_id, version as doc_version, split(version, '.')[offset(0)] as major_version, approval_date
    from {{ ref('policy_register') }}
    -- Policies, plus the one supporting document everyone must acknowledge: DOC-04 Electronic
    -- Monitoring Notice (POL-05 5.9, NY Civil Rights Law 52-c; added 2026-11-28, GOV-108).
    where (doc_type = 'policy' or doc_id = 'DOC-04') and status = 'approved'
),
staff as (
    select employee_id, department, hired_at
    from {{ ref('stg_hris_employees') }}
    where employment_status = 'active'
),
required as (
    select
        s.employee_id,
        s.department,
        p.doc_id,
        p.doc_version,
        p.major_version,
        greatest(p.approval_date, coalesce(s.hired_at, p.approval_date)) as assigned_on
    from staff s
    cross join policies p
),
received as (
    select employee_id, doc_id, split(doc_version, '.')[offset(0)] as major_version,
           min(acknowledged_on) as acknowledged_on,
           max(acknowledged_on) as last_acknowledged_on,
           string_agg(evidence, '; ' order by acknowledged_on) as evidence
    from (
        select employee_id, doc_id, doc_version, acknowledged_on, evidence
        from {{ ref('policy_acknowledgments') }}
        union all
        select employee_id, doc_id, doc_version, acknowledged_on,
               concat(evidence, ' [Simulated]') as evidence
        from {{ ref('stg_hris_policy_acknowledgments') }}
    )
    where acknowledged_on is not null
    group by 1, 2, 3
),
rule_dated as (
    select
        r.*,
        (
            select max(d) from (
                select d
                from unnest(generate_date_array(date_add(r.assigned_on, interval 1 day),
                                                date_add(r.assigned_on, interval 20 day))) as d
                where extract(dayofweek from d) not in (1, 7)
                order by d
                limit 10
            )
        ) as rule_due_on
    from required r
),
deadlines as (
    select doc_id, cast(major_version as string) as major_version, ack_deadline
    from {{ ref('policy_ack_deadlines') }}
),
dated as (
    select
        r.* except (rule_due_on),
        greatest(r.rule_due_on, coalesce(dl.ack_deadline, r.rule_due_on)) as due_on
    from rule_dated r
    left join deadlines dl
        on dl.doc_id = r.doc_id and dl.major_version = r.major_version
)
select
    concat(d.employee_id, '|', d.doc_id, '|', d.major_version) as ack_key,
    d.employee_id,
    d.department,
    d.doc_id,
    d.doc_version,
    d.major_version,
    d.assigned_on,
    d.due_on,
    a.acknowledged_on,
    a.last_acknowledged_on,
    date_add(a.last_acknowledged_on, interval 12 month) as next_due_on,
    a.evidence,
    case
        when a.acknowledged_on is not null and date_add(a.last_acknowledged_on, interval 12 month) < current_date() then 'expired'
        when a.acknowledged_on is not null then 'acknowledged'
        when current_date() > d.due_on then 'overdue'
        else 'pending'
    end as ack_status,
    a.acknowledged_on is not null and a.acknowledged_on <= d.due_on as on_time
from dated d
left join received a
    on a.employee_id = d.employee_id and a.doc_id = d.doc_id and a.major_version = d.major_version
