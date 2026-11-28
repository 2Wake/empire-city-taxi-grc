-- Who must complete which security training course, by when, and whether they have (POL-14 section 5.3;
-- GOV-110). Built like fct_policy_acknowledgments: derived daily, one row per active employee per
-- required course. SIMULATED completions come from HR's training feed (generator 0.6.0).
--   TRN-01 staff course: every active employee outside Driver Operations.
--   TRN-02 driver module: every active driver.
--   TRN-03 role training: staff with an active `raw` or `staging` grant (sensitive-access roles,
--          POL-14 section 3), due before that access is given (statement 9).
-- Due dates: staff employed when the courses opened, by the campaign deadline (2027-02-24, GOV-110);
-- later hires, 10 business days after starting (statement 8); TRN-03 assigned after launch, on the day
-- the access was granted. Overdue training goes to the manager and the VP People; after 30 days to the
-- CISO, who may suspend sensitive access (decision 2(b)). Each course is repeated every 12 months.
{% set campaign_deadline = "date '2027-02-24'" %}
with courses as (
    select course_id, version as course_version, launched_on, refresher_months
    from {{ ref('training_courses') }}
),
staff as (
    select employee_id, department, hired_at
    from {{ ref('stg_hris_employees') }}
    where employment_status = 'active'
),
sensitive as (
    select employee_id, min(date(granted_at, 'America/New_York')) as access_since
    from {{ ref('stg_iam_access_grants') }}
    where grant_status = 'active' and dataset in ('raw', 'staging')
    group by 1
),
required as (
    select s.employee_id, s.department, c.course_id, c.course_version, c.refresher_months,
           greatest(c.launched_on, s.hired_at) as assigned_on,
           s.hired_at <= c.launched_on as in_campaign
    from staff s
    join courses c
      on (c.course_id = 'TRN-02' and s.department = 'Driver Operations')
      or (c.course_id = 'TRN-01' and s.department != 'Driver Operations')
    union all
    select s.employee_id, s.department, c.course_id, c.course_version, c.refresher_months,
           greatest(c.launched_on, x.access_since) as assigned_on,
           x.access_since <= c.launched_on as in_campaign
    from staff s
    join sensitive x using (employee_id)
    join courses c on c.course_id = 'TRN-03'
    where s.department != 'Driver Operations'
),
done as (
    select employee_id, course_id, max(completed_on) as completed_on, max(score) as score
    from {{ ref('stg_hris_training_completions') }}
    group by 1, 2
),
as_of as (select max(_batch_date) as as_of_date from {{ ref('stg_app_trips') }}),
dated as (
    select r.*,
        case
            when r.in_campaign then {{ campaign_deadline }}
            when r.course_id = 'TRN-03' then r.assigned_on
            else (
                select max(d) from (
                    select d from unnest(generate_date_array(date_add(r.assigned_on, interval 1 day),
                                                             date_add(r.assigned_on, interval 20 day))) as d
                    where extract(dayofweek from d) not in (1, 7)
                    order by d limit 10
                )
            )
        end as due_on
    from required r
)
select
    concat(d.employee_id, '|', d.course_id) as training_key,
    d.employee_id,
    d.department,
    d.course_id,
    d.course_version,
    d.assigned_on,
    d.due_on,
    c.completed_on,
    c.score,
    date_add(c.completed_on, interval d.refresher_months month) as next_due_on,
    case
        when c.completed_on is not null and date_add(c.completed_on, interval d.refresher_months month) < a.as_of_date then 'expired'
        when c.completed_on is not null then 'completed'
        when a.as_of_date > d.due_on then 'overdue'
        else 'pending'
    end as training_status,
    c.completed_on is not null and c.completed_on <= d.due_on as on_time,
    if(c.completed_on is null and a.as_of_date > d.due_on, date_diff(a.as_of_date, d.due_on, day), null) as days_overdue,
    case
        when c.completed_on is not null or a.as_of_date <= d.due_on then null
        when date_diff(a.as_of_date, d.due_on, day) > 30 then 'ciso'
        else 'manager_and_vp_people'
    end as escalated_to
from dated d
cross join as_of a
left join done c using (employee_id, course_id)
