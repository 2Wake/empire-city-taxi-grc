-- Monthly overdue-review check (STD-01 section 9; GOV-112): every document in the Policy Register with
-- its next review date and whether that review is overdue or falls due within 60 days. Reported to the
-- CISO each month by the policy administrators. Drafts without a review date show as 'not_approved'.
with as_of as (select max(_batch_date) as as_of_date from {{ ref('stg_app_trips') }})
select
    r.doc_id,
    r.title,
    r.doc_type,
    r.owner_role,
    r.status,
    r.version,
    r.approval_date,
    r.next_review_date,
    case
        when r.status != 'approved' or r.next_review_date is null then 'not_approved'
        when r.next_review_date < a.as_of_date then 'overdue'
        when r.next_review_date <= date_add(a.as_of_date, interval 60 day) then 'due_within_60_days'
        else 'current'
    end as review_status,
    if(r.next_review_date < a.as_of_date, date_diff(a.as_of_date, r.next_review_date, day), null) as days_overdue
from {{ ref('policy_register') }} r
cross join as_of a
