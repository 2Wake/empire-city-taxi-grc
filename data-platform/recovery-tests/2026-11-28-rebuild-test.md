# Rebuild test 2026-11-28 (POL-15 statement 8; GOV-163)

First test of the [rebuild runbook](../docs/rebuild-runbook.md). Performed by the maintainer in the
Head of Platform / SRE role (`platform-sre`), with Claude Code, under the owner's blanket approval of
2026-11-28. Target dataset: `scratch` (not `raw`).

## What was rebuilt

- **Generator version:** `generator-v0.4.0` (every loaded `raw` row up to 2026-11-27 is 0.4.0), checked
  out into a separate git worktree.
- **Sample dates:** 2026-01-01 (the starting population, the largest batch), 2026-06-15 and 2026-11-20,
  with real TLC trips.
- **Tables:** all 11 generated tables present on those dates.

## Result

| Table | Rows in `raw` | Rows rebuilt | Only in `raw` | Only rebuilt | Checksum match |
|---|---:|---:|---:|---:|---|
| app_marketing_campaigns | 40 | 40 | 0 | 0 | yes |
| app_rider_segments | 12 | 12 | 0 | 0 | yes |
| app_riders | 2,015 | 2,015 | 0 | 0 | yes |
| app_trip_surveys | 63 | 63 | 0 | 0 | yes |
| app_trips | 2,756 | 2,756 | 0 | 0 | yes |
| fleet_drivers | 301 | 301 | 0 | 0 | yes |
| gov_planted_defects | 324 | 324 | 0 | 0 | yes |
| hris_employees | 519 | 519 | 0 | 0 | yes |
| iam_access_grants | 130 | 130 | 0 | 0 | yes |
| payments_financial_ledger | 138 | 138 | 0 | 0 | yes |
| payments_rider_cards | 1,809 | 1,809 | 0 | 0 | yes |
| **Total** | **8,107** | **8,107** | **0** | **0** | |

Compared by a fingerprint (`FARM_FINGERPRINT(TO_JSON_STRING(...))`) of every column except `_batch_date`
and `_generator_version`, per row (`EXCEPT DISTINCT` both ways) and as a table checksum (`BIT_XOR`).

**Also checked:** the code on the branch for generator 0.6.0 regenerates the same 8,107 rows for these
dates, apart from the version column, so the new acknowledgment and training features don't change history.

## Time and cost

- Started 12:37:50 UTC, finished 12:39:42 UTC: **about 2 minutes** for the sample (regenerate 6 s; load
  and compare about 1.5 min). A first comparison attempt failed on a quoting error in the shell and was re-run.
- A full rebuild of `raw` (331 days) is estimated at under 1 hour, which is well within the **RTO of
  2 business days**. **RPO:** the newest loaded day is reproducible, so data loss is at most the day not yet loaded,
  within 24 hours.
- Billed: 230 MB of queries, plus load jobs, which are free.
- Clean-up: the 11 `scratch.rt_*` tables were deleted, and the worktree and local batches removed.

## Limits of this test

- It was a sample of 3 dates, not a full rebuild. The next yearly test should rebuild a whole month.
- The reference tables (TLC sample and zones) and the observed `iam_role_access_tests` weren't part of it.
- The runbook was followed by its author, not by another person. Statement 7 asks that another authorized
  person can follow it; next year's test should be run by a delegate.

## Outcome

Passed. This completes the rebuild-test and runbook parts of the treatment for exception R-006
(GOV-153). R-006 stays open until the rest of its treatment is done: recovery codes held offline (F30,
GOV-142) and the first Atlassian export (F29, GOV-141; GOV-158).
