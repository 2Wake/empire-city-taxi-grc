# Data platform rebuild runbook (POL-15 statement 7)

How to rebuild ECT's data platform (`raw`, `staging`, `marts` in BigQuery) from the repository, if the
data is lost, corrupted or must be reloaded. Written so another authorized person can follow it: the
Head of Platform / SRE (`platform-sre`) or a delegate approved by the CISO. Treatment for exception R-006
(GOV-153); first test: [recovery-tests/2026-11-28-rebuild-test.md](../recovery-tests/2026-11-28-rebuild-test.md).

**Targets (POL-15):** RTO 2 business days, RPO 24 hours (the last daily run).

**Why a rebuild works:** every generated `raw` row is reproducible. The generator is deterministic: the same date and
the same generator version always give the same rows. Git tags `generator-vX.Y.Z` mark each version
(GOV-157), and every row carries `_generator_version`. Only three things are not generated: the TLC
sample (copied from public data), the taxi zones, and the observed access-check results
(`raw.iam_role_access_tests`, which can't be recreated and are lost in a full rebuild; their daily summary
is kept in each run record).

## Before you start

1. **Approval.** A rebuild of `raw` deletes and reloads tables. It needs the CISO's and the data owners' approval,
   recorded in Jira, and a `disposal_log.csv` entry if data is intentionally not restored (POL-13 statement 16).
2. **Access.** A Google account with BigQuery Data Editor on the target dataset and Job User on the project.
   Locally: `gcloud auth application-default login`.
3. **Tools:** `git`, `uv` (Python 3.12), `dbt` 1.12 with the BigQuery adapter, `bq`. See the root `CLAUDE.md`.
4. **Pause the daily run** so it doesn't load into a half-rebuilt dataset: GitHub → Actions → Daily data
   refresh → ⋯ → Disable workflow. Re-enable it at the end.
5. **Practise in `scratch` first.** The yearly test (statement 8) and any real rebuild start with a sample in
   the `scratch` dataset, compared with `raw` (step 6).

## Steps

### 1. Find which generator version made each day

```sql
SELECT _generator_version, MIN(_batch_date) AS first_day, MAX(_batch_date) AS last_day, COUNT(*) AS row_count
FROM `empire-city-taxi.raw.hris_employees`   -- repeat for any table if unsure
GROUP BY 1 ORDER BY 2;
```

If `raw` is gone, use the run records (`data-platform/run-records/`, rows per day) and the tag dates in git.

### 2. Recreate the reference tables (only if lost)

Run `data-platform/sql/01_tlc_yellow_trips_sample.sql` (about 6.8 GB scanned once, within the free tier) and
`02_tlc_taxi_zones.sql` in the BigQuery console, as each file's header describes.

### 3. Regenerate the batches, one version range at a time

For each version range from step 1, in a separate folder so your working copy isn't touched:

```bash
git worktree add /tmp/ect-rebuild-<version> generator-v<version>
cd /tmp/ect-rebuild-<version>/data-platform
uv sync --frozen
uv run ect-generate --start <first_day> --end <last_day>
```

Each version since 0.6.0 reads `dbt/seeds/governance/disposal_log.csv` and leaves out every record
disposed of under POL-13, so disposed data doesn't come back. For an older version, copy the current
disposal log into the worktree first. Each day's `output/<date>/manifest.json` has row counts and SHA-256 hashes.

### 4. Load

- **Into `scratch` (test):** load the `.jsonl` files into `scratch.rt_<table>` (see the test record for the
  script used), then compare (step 6).
- **Into `raw` (real rebuild):** `uv run ect-load --start <first_day> --end <last_day> --bulk` for the first range,
  then without `--bulk` for later ranges. Each day replaces only its own partition, so a re-run is safe.

### 5. Rebuild the models

```bash
cd data-platform/dbt && dbt build
```

### 6. Check the result

For each table and a sample of dates (or all dates), compare the row counts and a fingerprint of every row
except `_batch_date` and `_generator_version` between the rebuilt copy and the reference. The query used in
the first test is in the test record. Expect zero differences. Then:

- `dbt build` passes with the usual warnings only (compare with the last run record).
- The run record of a manual daily run (Actions → Run workflow) looks normal.

### 7. Finish

1. Re-enable the daily workflow.
2. Delete the `scratch` copies and the worktrees.
3. Record the rebuild: date, versions, days, row counts, checks, time taken against the RTO, and who approved,
   in `data-platform/recovery-tests/` (tests) or the incident ticket (real rebuilds), plus the WORKLOG.

## Cost

Generation and loading are free (load jobs don't count against the query quota). Comparisons scan only the
sampled partitions. The first test billed 230 MB, well within the 1 TB monthly free tier. Always set
`maximum_bytes_billed`.
