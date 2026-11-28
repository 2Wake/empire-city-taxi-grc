# Empire City Taxi — Data Platform

The living data behind the governance program. Each day the generator simulates one more
day of company life (hires, terminations, rider sign-ups, card changes, campaigns, ledger
postings and real NYC taxi trips) and the loader adds that day to BigQuery.

```
generator (Python + Faker) ──► output/<date>/*.jsonl ──► loader ──► BigQuery raw.<table>  (partition = that day)
         ▲                                                                       │
         └── real trips: raw.tlc_yellow_trips_sample (1% of NYC TLC 2022)        └──► dbt ► staging ► marts (next)
```

## Key ideas, in plain language

| Idea | What it means |
|---|---|
| **Repeatable** | The same date always produces exactly the same data, so any day can be rebuilt and any finding can be reproduced. (Tests check this.) |
| **Incremental, append-only** | Each day's batch holds only records created or changed that day, like a nightly extract from each source system. Nothing is deleted: a termination is a new row with status `terminated`. History is never overwritten. |
| **Safe to re-run** | Each day loads into its own partition. Loading the same day twice replaces that day rather than duplicating it. |
| **Real trips, fake people** | Trip times, distances, fares and zones are real 2022 NYC yellow-taxi trips, replayed on the matching weekday. Drivers and riders assigned to them are fictional. Card-paid trips are partly app bookings (with a rider); the rest are street hails (no rider). |
| **Planted defects with an answer key** | The generator plants data-quality defects (malformed last-4 values, missing emails, PII in survey comments, ...) and records every one in `gov_planted_defects`, without the bad value itself. Data-quality checks are scored against it. The real TLC data brings its own unplanted defects (negative fares, impossible distances). |
| **Fictional and safe values** | Phones use the 555 exchange, emails use `example.com` / `empirecitytaxi.example`. |
| **No full card, SSN or bank numbers** | From generator 0.4.0 ECT stores only what a real company would get back from its providers: the last 4 digits plus the payment processor's token for cards, and the last 4 digits for SSNs and payout bank accounts (POL-04, POL-11). The full numbers are said to stay with the payment, payroll and payout providers. |

## Raw tables

| Table | Source system | Classification | What changes over time |
|---|---|---|---|
| `hris_employees` | HR | Secret | Hires, terminations, annual review on March 1 (ratings, raises) |
| `fleet_drivers` | Fleet | Secret | Hires (onboarding → background check → active), suspensions, terminations |
| `app_riders` | Rider app | Confidential | Sign-ups, phone and address changes, account closures |
| `payments_rider_cards` | Payments | Secret (PCI) | Cards added and removed |
| `app_trips` | Dispatch | Confidential | ~1,000 real trips per day |
| `app_trip_surveys` | Rider app | Confidential | ~6% of app-booked trips |
| `payments_financial_ledger` | Payments | Sensitive | Prior month posted on the 3rd |
| `app_marketing_campaigns` | Marketing | Sensitive | New campaigns every ~2 weeks |
| `app_rider_segments` | Marketing | Internal | Size estimates refresh on the 1st |
| `gov_planted_defects` | Governance | Internal | Answer key for planted defects |
| `hris_policy_acknowledgments` | HR | Internal | Policy acknowledgments from 2026-11-28 (0.5.0) |
| `hris_training_completions` | HR | Internal | Security training completions from 2026-12-01 (0.6.0) |
| `tlc_yellow_trips_sample` | NYC TLC (public) | Public | Fixed one-time copy (`sql/01_…`) |
| `tlc_taxi_zones` | NYC TLC (public) | Public | Fixed one-time copy (`sql/02_…`) |

Every table carries the labels from the [Labeling Standard](../01-governance-program/governance/labeling-standard.md) and has two extra columns: `_batch_date` (the day it arrived) and `_generator_version` (the code that made it).

The simulation starts on **2026-01-01** with 150 office staff, 300 drivers, 2,000 riders and 1,800 cards.

## Commands

Run from this folder (`data-platform/`).

| Task | Command |
|---|---|
| Run the tests | `uv run pytest` |
| **Daily run:** catch up every missing day through yesterday (generate + load) | `uv run ect-daily` (add `--dry-run` to preview) |
| **Acknowledgment summary**: people done and left, and the daily comment on blog 950312 (after `dbt build`) | `uv run ect-ack-summary` (`--post` to post; setup part K) |
| Write a run record (after `ect-daily` and `dbt build`) | `uv run ect-record` |
| **Security review** (POL-09): check yesterday's audit logs for the Appendix A alerts | `uv run ect-security-review` (`--day 2026-11-24` for one day; `--check` exits 1 on alerts) |
| **Watchdog** (POL-09): alert if today's run record is missing after 12:00 New York | `uv run ect-watchdog` |
| **Configuration check** (POL-10 st. 4; monthly in Actions): read-only check of cloud and repository settings, writes `config-checks/<date>.md` | `uv run ect-config-check` (`--check` exits 1 on findings) |
| **Build-tools manifest** (POL-10): regenerate `build-tools-manifest.md` after changing actions, dbt pins or `uv.lock` | `uv run ect-manifest` (`--check` to verify) |
| Generate yesterday | `uv run ect-generate` |
| Generate one day / a range / everything | `uv run ect-generate --date 2026-11-23` · `--start … --end …` · `--backfill` |
| Generate without trips (offline) | add `--no-trips` |
| Preview a load (changes nothing) | `uv run ect-load --date 2026-11-23 --dry-run` |
| Load into BigQuery | `uv run ect-load --date 2026-11-23` |
| First-time backfill of a range (one job per table) | `uv run ect-load --start 2026-01-01 --end 2026-11-23 --bulk` |

## Cost

- **One-time:** `sql/01_tlc_yellow_trips_sample.sql` scans ~6.8 GB, and `sql/02_tlc_taxi_zones.sql` ~2 MB.
- **Daily:** loads are free. The trip fetch reads one small partition (billed at the 10 MB minimum) and is capped at 1 GB by `maximum_bytes_billed`.
- **Storage:** after the 327-day backfill, all of `raw` is about 170 MB (trips 91 MB plus the 76 MB TLC sample). Roughly 2% of the 10 GB free tier after a year.

## Not yet done

Column descriptions and the description gap register; planted label gaps; Phase 1–4 tables; council scenario defects (Phase 3).

## Daily schedule

GitHub Actions runs `ect-daily`, then `dbt build`, then `ect-ack-summary --post`, then `ect-security-review`, then `ect-record` every morning, and commits the run record to `run-records/`. If the security review raised an alert or couldn't run, the last step fails the run after the record is committed, so GitHub emails the maintainer. A separate **watchdog** workflow (`.github/workflows/watchdog.yml`) checks at 12:05 New York that today's run record exists. A **Google-side backup** (a BigQuery scheduled query running as `ect-watchdog`, `sql/watchdog_check.sql`, setup part J) checks at 12:05 New York that `raw` and `marts` were updated today, so a late or missing run is caught even when GitHub's scheduler is the problem; a Cloud Monitoring log alert emails the maintainer when it fails (BigQuery's own failure email doesn't reach a person when the query runs as a service account). One-time setup: [docs/github-actions-setup.md](docs/github-actions-setup.md) (part H for the log reader account).

**Monitoring limits:** the review reads Google Cloud audit logs only (GitHub and Atlassian logs are reviewed monthly by hand, POL-09 statement 17). The GitHub watchdog runs on the same scheduler as the daily run (both started 7 to 10 hours late on 2026-11-25 and 26, GOV-123); the Google-side backup covers that. Run records show role names or `unknown-identity-<hash>`, never personal emails or IP addresses, because the repository is public.
