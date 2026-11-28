-- Every compliance finding with its owner, steward, due date and status (POL-02 st. 19; POL-03
-- compliance st. 1-2; GOV-111). Built from the daily history (fct_compliance_findings_daily):
--   open      seen in the latest run and not yet due;
--   overdue   seen in the latest run and past its due date (due_business_days after first seen);
--   resolved  not seen in the latest run; resolved_on is the first day it was no longer seen.
-- Owners are routed by the finding_routing seed; classification findings go to the column's own
-- data owner and steward from the register. The council reviews the open and overdue list monthly.
with history as (select * from {{ ref('fct_compliance_findings_daily') }}),
latest as (select max(run_date) as latest_run from history),
spans as (
    select rule_id, record_id, any_value(table_name) as table_name, any_value(column_name) as column_name,
           any_value(severity) as severity, array_agg(detail ignore nulls order by run_date desc limit 1)[safe_offset(0)] as detail,
           min(run_date) as first_seen, max(run_date) as last_seen
    from history
    group by 1, 2
),
routing as (select * from {{ ref('finding_routing') }}),
routed as (
    select s.*,
           array_agg(struct(r.owner_role, r.steward_role, r.due_business_days, r.route)
                     order by length(r.rule_prefix) desc limit 1)[offset(0)] as rt
    from spans s
    join routing r on starts_with(s.rule_id, r.rule_prefix)
    group by s.rule_id, s.record_id, s.table_name, s.column_name, s.severity, s.detail, s.first_seen, s.last_seen
),
register as (
    select concat(layer, '.', table_name, '.', column_name) as record_id, data_owner, data_steward
    from {{ ref('column_classification_register') }}
),
dated as (
    select r.*,
           array(select d from unnest(generate_date_array(date_add(r.first_seen, interval 1 day),
                                                          date_add(r.first_seen, interval 90 day))) as d
                 where extract(dayofweek from d) not in (1, 7) order by d)[offset(r.rt.due_business_days - 1)] as due_on
    from routed r
)
select
    concat(r.rule_id, '|', r.record_id) as finding_key,
    r.rule_id,
    r.record_id,
    r.table_name,
    r.column_name,
    r.severity,
    r.detail,
    if(r.rt.owner_role = 'column-owner', coalesce(g.data_owner, 'data-governance-manager'), r.rt.owner_role) as owner_role,
    if(r.rt.steward_role = 'column-steward', coalesce(g.data_steward, 'data-governance-manager'), r.rt.steward_role) as steward_role,
    r.rt.route as action,
    r.first_seen,
    r.due_on,
    r.last_seen,
    case
        when r.last_seen < l.latest_run then 'resolved'
        when l.latest_run > r.due_on then 'overdue'
        else 'open'
    end as status,
    if(r.last_seen < l.latest_run, date_add(r.last_seen, interval 1 day), null) as resolved_on
from dated r
cross join latest l
left join register g using (record_id)
