{{ config(materialized='incremental', incremental_strategy='insert_overwrite',
          partition_by={'field': 'run_date', 'data_type': 'date'}) }}
-- One row per compliance finding per day it is seen (GOV-111). Kept as history, so the tracker can tell
-- when a finding first appeared and when it was resolved. Covers the rules an owner must act on:
-- access (ACC), HR (HR), card terminals and payment page (PCI) and classification (CLS). Data-quality
-- rules on source data (DQ, T, REF) stay in fct_dq_findings and the scorecard.
with today as (select current_date('America/New_York') as run_date)
select t.run_date, f.rule_id, f.record_id, f.table_name, cast(null as string) as column_name, f.severity,
       cast(null as string) as detail
from {{ ref('fct_dq_findings') }} f cross join today t
where regexp_contains(f.rule_id, r'^(ACC|HR|PCI)-')
union all
select t.run_date, c.rule_id, concat(c.layer, '.', c.table_name, '.', c.column_name) as record_id,
       c.table_name, c.column_name, 'Medium' as severity, c.detail
from {{ ref('fct_classification_findings') }} c cross join today t
