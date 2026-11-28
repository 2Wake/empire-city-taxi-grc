# CLAUDE.md

Context and working agreements for Claude Code sessions in this repository.

## Project

A portfolio GRC program for **Empire City Taxi Co. (ECT)**, a fictional NYC taxi operator. See [`README.md`](README.md) and [`00-company/`](00-company/).
- Projects 1 (data governance) and 2 (SOC 2 / ISO audit) are built.
- Projects 3 (GRC automation) and 4 (AI in GRC) are planned.
- The current work is a **living data platform**: synthetic company data generated daily, governed end to end.

**Read [`WORKLOG.md`](WORKLOG.md) first.** It holds the decisions, their rationale, the backlog, and what's next.

## Working agreements (always follow)

1. **The owner is not an engineer.** Explain every step in plain language, give exact click paths and values, and warn about easy mistakes, such as unit dropdowns.
2. **Cloud and account changes are made by the owner in the web UI.** This covers Google Cloud, GitHub settings and Collate. Give step-by-step instructions instead of running CLI or API changes. **Never change a setting without explicit approval.** Read-only checks are fine; say what each one does.
3. **Git: every change reaches `main` through a pull request** (owner decisions 2026-11-24; POL-07 v1.1). Claude commits on a feature branch, pushes it, and **creates the PR with `gh pr create`**, with the full description at creation, following `.github/pull_request_template.md`. The description must include everything a reviewer needs: summary, why, every file changed and how, the commits, the evidence behind any claim, change type, DOC-01 scope check, testing, risk and rollback, what was deliberately *not* changed, and full links to related Jira and Confluence items. (The earlier flow, where the owner created the PR and pasted the description, failed three times: PRs #3, #5 and #6 opened with the blank template.) Claude then posts its review as a PR comment (`gh pr review --comment`). It's a review, not an approval: Claude acts through the owner's GitHub account, and GitHub doesn't let an author approve their own PR. **The owner approves by merging in GitHub, or by telling Claude to merge that PR.** **Before every push to a PR branch, check the PR is still open** (`gh pr view N --json state`); if it's merged, start a new branch from `origin/main` and open a new PR. Commits pushed to a merged PR's branch never reach `main` (PRs #5 and #7; it was not GitHub lag). Once Claude says a PR is ready, it adds no more commits to it; later work goes in the next PR. Before saying a PR is ready to merge, check it's open and its commit list matches the branch (`gh pr view N --json state,commits`). When the owner tells Claude to merge, use `gh pr merge N --merge --match-head-commit <branch tip>`, which refuses if the PR doesn't hold exactly that commit. Never push or merge to `main` without that go-ahead. The only direct pushes are the daily run's run-record commit and the monthly configuration check's result file (`data-platform/config-checks/`, from 2026-11-28; GOV-159).
4. **Log every meaningful step in `WORKLOG.md`** (newest first): done, decisions with rationale, risks, next steps. Keep the backlog at the top current.
5. **Jira and Confluence (Atlassian MCP):** Claude may **create Confluence pages directly**, and posts a short summary of each page in the chat. Claude **drafts Jira tickets** for the owner to approve before creating them. Every ticket has these sections: **Description**, **Why it matters**, **Potential blockers**, **Intended outcome**. **Before closing a ticket (moving it to Done), add a closing comment** with two parts: *What happened* (a summary of the work and where it lives) and *Open items* (anything left, deferred or found; "None" if nothing).
   - Site: `empire-city-taxi.atlassian.net` (cloudId `7afb79ce-b26f-4945-b14a-8b27a4be498e`). Jira space **GRC Program**, key `GOV` (program work: policies, findings, remediation; renamed from ECT GRC on 2026-11-24). Jira space **Security Incidents**, key `SI` (incident reports, from 2026-11-24; owner-created). Confluence space **Empire City Taxi Governance**, key `ECTG` (space id `327685`).
   - **Where things live:** Confluence holds policy text, minutes and process docs. Jira holds planning, findings, remediation and audit requests. **Confluence is the single source of truth for policy text: no copies in the repo** (owner decision 2026-11-24; STD-01 v2.0). The repo holds only what the pipeline reads (policy register extract, acknowledgments, control framework, issue register as dbt seeds); the register seed is an extract of the Confluence page, never edited on its own. **Every policy approval or change is announced in a Confluence blog post written as an email to staff** (From/To/Date/Subject; what was approved; what to do and by when; acknowledge by commenting on the post), within 10 business days of approval (STD-01 s11; owner decision 2026-11-24, replacing the earlier "no announcement post"). Simulated reviews, approvals and acknowledgments are marked *[Simulated]*, dated the day they're recorded, never backdated. `WORKLOG.md` stays the decision log.
6. **Integrity:** synthetic data only, apart from the public NYC TLC trips. All people are fictional. Never commit keys, credentials, billing account IDs or personal emails.

## Environment

| Item | Value |
|---|---|
| GCP project | `empire-city-taxi` (billing on; a ~30 GB/day query quota and a $5 budget alert are set) |
| BigQuery datasets | `raw`, `staging`, `marts` (US; no table expiry; labeled) |
| Tools | `gh`, `gcloud`, `bq`, `uv` in `/opt/homebrew/bin`. `dbt` (1.12 + BigQuery adapter) in `~/.local/bin`. `bq` also needs `/opt/homebrew/share/google-cloud-sdk/bin` on `PATH`. |
| Python | Use 3.12 through `uv`. The system Python is 3.9; don't use it for project code. |
| Laptop | 8 GB RAM. Don't plan heavy local services (OpenMetadata, Airflow, Metabase). |

## Architecture (decided)

- **Flow:** Faker generator (Python) → GitHub Actions (daily) → BigQuery `raw` → dbt → `staging` → `marts` → Collate (catalog) and Looker Studio.
- **Code:** [`data-platform/`](data-platform/) (generator, loader, one-time SQL, tests; see its README). Run commands from that folder with `uv run`, and run `uv run pytest` after any change. Bump `GENERATOR_VERSION` when output changes, and after that PR merges, tag the merge commit `generator-vX.Y.Z` (owner OK each time; GOV-157).
- **Daily run:** `.github/workflows/daily-refresh.yml` (05:17 UTC; backup starts 08:17 and 11:17 skip if today already refreshed) → `ect-daily` (catch up missing days) → `dbt build` → `ect-ack-summary` (daily acknowledgment comment on blog 950312) → `ect-record` (run record in `data-platform/run-records/`). Monthly: `config-check.yml` runs `ect-config-check` (read-only; results in `data-platform/config-checks/`). Setup: `data-platform/docs/github-actions-setup.md`. Rebuild: `data-platform/docs/rebuild-runbook.md`.
- **dbt:** [`data-platform/dbt/`](data-platform/dbt/). Run `dbt build` from that folder. Staging views keep defects as they are. History is derived from the raw change logs (not snapshots). Data-quality rules (`dq_*`) are warnings; structural tests are errors.
- **Datasets by layer, domain by label.** Raw tables carry a source-system prefix: `hris_`, `fleet_`, `payments_`, `app_`, `tlc_`. dbt models are `stg_*`, `dim_*`, `fct_*`.
- **`raw` is append-only.** Lifecycle changes arrive as new full-record versions, and history is derived from them in dbt (`stg_*_history`).
- **The generator is deterministic**: the same date always produces the same output. IDs are prefixed (`DRV10042`, `EMP10001`, `RDR…`, `VEH…`).
- **Governance records** (issues `GV-###`, decisions `GV-D-###`, org, ownership) live as repo files and load as dbt seeds.
- **Every governance conflict scenario is backed by a defect planted in the data.** Planted defects and documentation and label gaps are tracked in answer-key or gap-register files.

## Cost rules

Stay in the BigQuery free tier (1 TB of queries and 10 GB of storage per month):
- Always set `maximum_bytes_billed` on queries.
- Partition tables by date.
- Never `SELECT *` on the public taxi tables.
- No Cloud Composer, Cloud SQL, or scheduled Dataplex DQ scans.

## Governance model

The user leans toward a **federated (hub-and-spoke)** model. The hub (Data Governance Manager) owns standards, tooling, the scorecard and reporting. Domain owners and stewards own their rules, definitions and fixes. **DQ rules are authored by stewards and approved by owners**; hub-drafted rules are proposals until signed off.

## Governance standards (source of truth)

All in `01-governance-program/governance/`:

| File | Defines |
|---|---|
| `data-classification-standard.md` | Five tiers: **Secret → Confidential → Sensitive → Internal → Public**. `marts` is capped at Sensitive. |
| `labeling-standard.md` | Required labels, the domain register, formatting rules |
| `classification-register.md` | How column classification is managed. The register and its answer key are dbt seeds in `data-platform/dbt/seeds/governance/`. (`column-classification-map.csv` is the superseded Project 1 map.) |
| `data-ownership-model.md`, `governance-org-structure.md`, `data-governance-council-charter.md` | Roles, named people, council, RACI |

Labels and data reference **role slugs**, never people's names.
