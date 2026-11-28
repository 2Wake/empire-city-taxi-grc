-- SIMULATED security awareness training completions (generator 0.6.0 onward): one row per passed quiz.
select
    *,
    date(completed_at, 'America/New_York') as completed_on
from {{ source('raw', 'hris_training_completions') }}
