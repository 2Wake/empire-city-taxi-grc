# Empire City Taxi GRC — Work Log

Running log of all work, decisions and open items. It's the source for progress summaries and status updates. Newest entries at the top. Updated after every meaningful step (see [`CLAUDE.md`](CLAUDE.md)).

---

## 📋 Backlog

- [x] **Phase 0: generator framework.** Built, tested, and backfilled into `raw` (2026-01-01 → 2026-11-23).
- [ ] **Reference-data issue:** raise REF-01 to REF-03 as a governance issue (reference domain owner: Data Governance Manager) in the issue register.
- [ ] **Remediate the classification scenarios** (S01–S12) through the council process, starting with GV-003 (S01). Watch KPI #2 rise from 72.5%.
- [ ] **Push classifications out:** Knowledge Catalog aspects (GOV-167, after the council decides STD-02 D2 and D3); optionally BigQuery policy tags on Secret columns (UI, owner).
- [ ] **Table and column descriptions.** Raw-table schema files, plus dbt `.yml` with `persist_docs`. Leave about 10–15% blank on purpose, tracked in a documentation-gap register, and fill them in a later remediation sprint.
- [ ] **Labels on tables:** applied in code on `raw`, `staging` and `marts`. **Remaining:** planted label gaps, tracked in the gap register.
- [ ] **Council operations.** Issue register (`GV-###`) and decision log (`GV-D-###`) as dbt seeds. Agendas and minutes in Confluence (page 1048579), if the council adopts the charter amendment on 12-01.
- [ ] **Phases 1–4 tables** (see the 2026-11-23 design review entry below).
- [x] **GitHub Actions daily refresh:** live since 2026-11-24. Runs daily at 05:17 UTC (00:17 New York; moved from 05:30 New York on 2026-11-27, GOV-123), keyless, and writes run records to `data-platform/run-records/`.
- [ ] **Access control:** simulated access live (ACC-01–07). The 79 unclassified new columns stay as an audit finding (don't fix). Real role accounts and the daily access check built (2026-11-24); access logs come with Phase 2.
- [x] **Atlassian (Jira + Confluence):** site, MCP and docs/tickets split all done (2026-11-24).
- [ ] **Policy set (SOC 2 + ISO 27001 + PCI DSS) + policy register:** tracked in Jira epic GOV-1. Then a **Common Control Framework** (CCF) as dbt seeds mapping policies → controls → frameworks → automated checks.
- [ ] **DQ rule ownership:** add `proposed_by` (steward), `approved_by` (owner) and `approval_status` to `dq_rules.csv`. The 23 current rules are hub-drafted proposals awaiting steward and owner sign-off.
- [ ] **Council roles and responsibilities (federated model):** flesh out each council member's duties, decision rights and time commitment; hub vs. domain (spoke) responsibilities; steward duties including DQ rule authoring.
- [x] ~~Collate~~: dropped 2026-11-25 (company email and wait list; connecting needs a key). Replaced by Knowledge Catalog.
- [ ] **Knowledge Catalog (STD-02, DRAFT v0.3):** council decides D2 to D4, then the one-time import and daily extract (GOV-167), Looker Studio tables, and a DOC-02 entry. Lineage cost check on or after 2026-12-02 (GOV-168).
- [ ] **First council meeting, Tuesday 2026-12-01** (agenda and review pack: Confluence 1015810; Jira GOV-171). After it: write the minutes, log decisions as `GV-D-###`, revise STD-02 to v0.3, move the charter to Confluence if adopted, and update the register for the 30 proposed rows.
- [ ] **Monitoring gaps (R-003, to 2027-01-31):** the Google-side watchdog is live and tested (GOV-170 Done). The daily run starts at 05:17 UTC with backup starts at 08:17 and 11:17 UTC, which skip if today is already refreshed (2026-11-28). GitHub dropped the 11-27 run entirely. If it keeps missing days, consider starting the run from Google's side.
- [ ] **Deadlines:** O7 log lock (GOV-94; lock between 12-26 and 12-31) and the first Atlassian export (GOV-158), both by 2026-12-31. Training campaign due 2027-02-24 (R-005 expires 01-31: renew or close). Vendor due diligence (R-004) and R-008 page change control by 02-28. Done 11-28: DOC-03, rebuild test, training courses. **12-09:** policy and DOC-04 acknowledgments (blog 950312; GOV-107, GOV-108).
- [ ] **Register approvals:** 30 rows still `proposed`. On the 12-01 agenda (item 4.3).
- [ ] **Clean up merged branches** on GitHub (`five-tier-classification`, `governance-council`). The user asked to keep them for now.

---

## 2026-11-28 — First-year records: GOV-90 and GOV-81 subtasks (generator 0.6.0, checks, Confluence records)

Owner, 2026-11-28: "Try to complete all subtasks under GOV-90 ... Let's try to get all subtasks under GOV-81 completed too. You have my blanket approval on everything." Non-blocking repo work goes in one combined PR (`first-year-records`).

### Repo (this PR)
- **Generator 0.6.0** (deterministic; history unchanged, checked against the 0.4.0 rebuild):
  - training completions from 2026-12-01 (`raw.hris_training_completions`; TRN-01 staff, TRN-02 drivers, TRN-03 staff with `raw` or `staging` access; campaign due 2027-02-24, new hires 10 business days);
  - planted defect `driver_activated_before_check` from 2026-12-01 (10% of new drivers; check HR-01);
  - disposed records (`disposal_log.csv`) are never generated again (GOV-162; first entry DSP-0001, the 11-25 column rebuild).
- **dbt:**
  - `stg_hris_training_completions`, `fct_training_completions` (status, days overdue, escalation; GOV-110, GOV-161);
  - new checks **HR-01 to HR-04** (POL-14) and **PCI-01 to PCI-03** (POL-04 st. 22 and 23; GOV-156);
  - ACC-02 and ACC-03 lined up with POL-02's deadlines (GOV-79; live counts unchanged, 2 and 2);
  - `fct_policy_review_status`: the monthly overdue-review check (GOV-112);
  - `fct_compliance_findings_daily` (history) and `fct_findings_tracker`: every ACC, HR, PCI and CLS finding with owner, steward, due date and status, routed by the `finding_routing` seed (GOV-111). Run on live data with stand-ins: 306 open findings, each with an owner and due date;
  - `fct_policy_acknowledgments`: the yearly re-acknowledgment cycle (`next_due_on`, status `expired`; GOV-107);
  - seeds: `pci_terminals` (166), `pci_terminal_inspections` (3 terminals missed the November round), `payment_page_scripts` (SCR-04 unapproved), `training_courses` (Confluence pages), `disposal_log`, `finding_routing`, `vendor_inventory` (DOC-03 extract); `policy_register` with DOC-03, DOC-05 to DOC-09 and POL-09 v1.1;
  - 17 classification rows (proposed) for the training tables, in the register and answer key.
- **New commands:**
  - `ect-config-check` (GOV-159): read-only check of IAM, keys, Data Access logs, dataset labels, log retention, the `main` ruleset, action pinning and Dependabot alerts. Monthly workflow `config-check.yml`; setup part L (owner gives `ect-monitor` 3 read roles). First run 2026-11-28: 8 ok, 2 findings (no PR rule on `main`, GOV-77; actions not pinned to commits, F14);
  - `ect-manifest` (GOV-160): `build-tools-manifest.md`, kept current by a test.
- **Docs and records:**
  - `docs/rebuild-runbook.md` and `recovery-tests/2026-11-28-rebuild-test.md` (GOV-163): 8,107 rows rebuilt from tag 0.4.0 into `scratch`, 0 differences, about 2 minutes, 230 MB;
  - SOC 2 corrections: BC-01 (rebuild, no DR region), BC-02 Partially implemented; PBC-019 Not collected, PBC-020 collected 2026-11-28;
  - `access-control-policy.md` replaced by a pointer to POL-02 (GOV-78);
  - vendor tool README: how its four tiers map to POL-12's three (GOV-99).
- pytest: 39 passed. `dbt parse` and compile pass.

### Confluence (created directly) [Simulated where marked]
- **Security Training** (1114150) with TRN-01 (1015888), TRN-02 (1015904), TRN-03 (1114166), and the IR role training record (1114214; GOV-109).
- **DOC-03 Vendor Inventory** (1015920; 14 vendors: 6 Critical, 7 High, 1 Low; GOV-154).
- **DOC-05 Cryptography Inventory** (1048609; GOV-155). **DOC-06 Obligations Register** (950349; GOV-118).
- **DOC-07 BIA** (950369), **DOC-08 BC/DR Plan** (1015944) with the **Manual Dispatch Procedure** (1015967), **Legal Holds and Deletion Requests** (1114198) (GOV-164).
- **Tabletop 2026-11-28** (1015983; POL-08 and POL-15; GOV-91, run early). Confirms F6 (no IR plan, no communications lead); missed: no processor contact.
- **2026 Annual Risk Assessment** (950389; GOV-92): new risks **R-007** (GOV-174, Medium 9) and **R-008** (GOV-175, High 12, card-entry page scripts). R-003 and R-006 re-scored to Medium; exceptions still run to expiry.
- **DOC-09 Targeted Risk Analyses** (1114232; GOV-117).
- **How to onboard and offboard a driver** (1114182; GOV-103).
- **POL-09 v1.1** (minor; GOV-95): GitHub's security log covers 90 days; the Atlassian Free plan has no Jira or Confluence audit log.
- **STD-03** (1015999) and **STD-04** (1048653) drafts v0.2 (GOV-80): numbers proposed for council item 4.4.
- **Policy Register v20**; announcement blog 1114286 (training from 12-01; the new records).

### Decisions (blanket approval)
- **GOV-94 lock:** recommend locking `_Default` (option A) after the 30-day trial ends 2026-12-25; the owner locks it in the console (irreversible) between 12-26 and 12-31.
- **Crypto inventory** lives in Confluence (DOC-05), not a seed.
- **The tabletop was run early** (11-28, not May 2027). Next by 2027-11-28; the May 2027 date stays for testing the GOV-88 plan.

### Corrections
- The earlier note "no Dependabot" was wrong: Dependabot alerts have been on since 2026-11-25 (POL-10). The real gap is action pinning (F14). `ect-config-check` checks both.
- R-006 isn't closed by the rebuild test alone: offline recovery codes (F30) and the Atlassian export (F29) remain.

### Findings recorded, not fixed
- `raw` and `staging` dataset labels still say `classification: secret` (no Secret data since 11-25).
- Atlassian Free plan: no audit log (POL-09 st. 13 can't be met for Jira and Confluence).
- R-005 expires 2027-01-31 but the training campaign is due 2027-02-24: renew the exception or close it on completion.
- TRN-03 shows overdue at once for new grants (by design: training before access).
- Creating a service account raises no alert; governance seeds aren't in the classification register (CLS-01).
- POL-14 5.3 calls training records a "repository data file"; they're now a raw feed (needs a minor revision).

### Next
- Owner: merge the PR, then tag `generator-v0.6.0`. Setup part L (3 roles for `ect-monitor`). GOV-77 ruleset. GOV-158 export. GOV-94 lock between 12-26 and 12-31.
- 11-29: check the first run with backup starts and the first daily comment.
- 12-01: council (per the private script), then GOV-80 numbering, GOV-166, GOV-167, GOV-171. 12-02: GOV-168 cost check.

---

## 2026-11-28 — Simulated policy acknowledgments and the daily summary comment (generator 0.5.0)

### Decisions
- **Owner, 2026-11-28:** don't post one comment per acknowledgment (8,432 would be too many). Post **one comment a day** with how many people have acknowledged and how many are left, and a **final count** once each deadline passes. "Build the acknowledgment simulation."

### Done (this PR)
- **Generator 0.5.0:** new raw table `hris_policy_acknowledgments` (People domain, Internal, owner `vp-people`, steward `hr-data-steward`).
  - From `ACK_START` = 2026-11-28, each active employee acknowledges all 16 documents (POL-01 to POL-15 plus DOC-04) in one action, on a day drawn from `ACK_WEIGHTS`:
    - **staff** comment on blog 950312 on business days, with the deadline at day 7;
    - **drivers** use the ECT Driver app any day, with the deadline at day 11.
  - About 88% are on time and 10% late (up to 10 business days, so the council item 4.5 escalation steps have cases). 2% never acknowledge.
  - New hires count from their hire date.
  - Days before 11-28 are unchanged, because 11-27 and earlier are already loaded.
  - The document list is fixed in `config.py` so a later register edit can't change history.
- **Offline dry run from 11-27 to 12-31:** 45 drivers on Saturday 11-28 and 89 people on Monday 11-30. 462 people are done by 12-09 and 8 never acknowledge.
- **dbt:**
  - `stg_hris_policy_acknowledgments` (adds the New York date) with tests;
  - `fct_policy_acknowledgments` now takes the earliest acknowledgment from the seed (approvers' and reviewers' comments) or HR's feed, and the feed's evidence is marked [Simulated];
  - 19 classification rows were added as **proposed** (`hr-data-steward`): raw 9 plus staging 10, all Internal. They show as CLS-03 findings until VP People approves them, which goes to the next monthly catalog review. The answer key has the same rows.
- **`ect-ack-summary`** (new step after dbt):
  - It counts **people**: done (every required document acknowledged), left, and overdue. It also counts documents.
  - On the first run after a group deadline (12-09; 12-14 for DOC-04), it adds "N of M people due that day met it".
  - It writes `output/ack_summary.json`, and `ect-record` adds a "Policy acknowledgments (simulated)" section with the comment text.
  - With `--post` it posts the comment on blog 950312, **once per day** (it checks for today's title first).
  - It never fails the run.
  - Query checked on the live mart: 10 MB billed (the minimum), with `maximum_bytes_billed` set.
- **Setup part K (owner):** an Atlassian API token plus GitHub secrets `CONFLUENCE_USER` and `CONFLUENCE_API_TOKEN`. Until then, the run record says "Not posted".
- pytest: 34 passed (2 new). `dbt parse` and compile pass. The mart SQL dry-run passed with a stand-in for the new table, which the first run creates.

### Next
- **After merge:** tag `generator-v0.5.0` (owner OK, GOV-157 process).
- The first run with 0.5.0 loads 11-28: 45 driver acknowledgments.
- Then the owner does part K, or Claude posts the summary from the run record by hand until then.

---

## 2026-11-28 — Security alerts now say when, who, what changed and how to triage

### Done
- **Owner feedback:** the failed step's message ("ALERT SEV3 ... maintainer, SetIamPolicy on project (x1)") had no date, didn't say what changed, and didn't say what to do. A non-engineer couldn't triage from it.
- **`ect-security-review --check` now prints, for each alert:**
  - **What:** the alert;
  - **When:** UTC and New York time;
  - **Who:** the identity;
  - **Change:** for IAM changes, the roles added or removed and for whom, taken from the audit log's policy delta (for example "added bigquery.jobUser, bigquery.metadataViewer to ect-watchdog").
  - It then gives the three triage steps (POL-09 statement 15; incidents under POL-08) and the run record file.
- **The same table goes on the run's summary page in GitHub** (`GITHUB_STEP_SUMMARY`), so it's visible without opening the step log.
- **Public-safe names:** Google service agents show as `google-service-agent (<service>)`, never with the project number. People still show only as a role or a hash.
- **Tested** on the real 11-27 logs (local, read-only): both alerts now show their time and change. pytest: 32 passed (2 new).

---

## 2026-11-28 — Backup start times for the daily run; GOV-169 closed; council item 4.5 (acknowledgment consequences)

### Done
- **Manual run** (owner, 06:41 New York, run 46141088504): loaded 11-26 and 11-27, and dbt passed.
  - The security review covered 11-26 and 11-27 and raised **2 alerts**, both on 11-27 and both expected watchdog setup:
    - 09:23 UTC: the maintainer gave `ect-watchdog` BigQuery Job User and Metadata Viewer (setup J1);
    - 09:30 UTC: Google's service-agent manager gave the BigQuery Data Transfer service agent its role, which happens automatically with the first scheduled query.
  - Triage ticket drafted for the owner's approval.
- **Backup start times (this PR):**
  - `daily-refresh.yml` adds cron 08:17 and 11:17 UTC, plus a `check` job: a scheduled start stops straight away if a run of the workflow already **refreshed today** (New York date).
  - "Refreshed" means its dbt step succeeded. The overall result isn't used, because it fails on purpose when the review raises alerts.
  - Runs already queue one at a time (`concurrency`), so a backup waiting behind a full run sees it and stops. Manual runs always go ahead.
  - **Why:** GitHub delayed the schedule 9 to 10 hours on 11-25 and 11-26, dropped 11-27, and hadn't started 11-28 by 11:41 UTC (GOV-123).
- **GOV-169 closed** with a closing comment: triage done on 11-27, and the case fix (PR #15) was used by today's run.
- **Council agenda 1015810 v5:** new item 4.5, consequences for not acknowledging policies. Today the only step is reporting to the manager and the VP People, with no escalation and no effect on access.
  - Options A (reminders only), **B (steps, proposed)** and C (hard stop).
  - **The owner set Option B's timings:** a reminder on the due date; the VP People at **5 business days** overdue; the CISO at **10 business days**, who may suspend access beyond email and HR self-service (drivers can't go online). The council recommends; the VP People and CISO revise POL-05 or POL-14.
- **Acknowledgment reporting** (owner decision): no per-person comments. One summary comment a day on blog 950312 (done and left), and a final summary after each deadline (12-09 policies, 12-14 DOC-04). How the simulated acknowledgments are produced is waiting for the owner's OK.

### Tested
- The `check` logic was run read-only against the real run history:
  - **11-26:** skip (run 45885971310's dbt step passed).
  - **11-27:** run (nothing that day).
  - **11-28:** skip (today's manual run).
  - **A manual start:** always runs.

### Found (left as findings)
- **The security review doesn't alert on a new service account** (`CreateServiceAccount`, `ect-watchdog` at 09:22 on 11-27). The account itself was expected. Whether creating a service account should alert is a question for POL-09 Appendix A.

---

## 2026-11-28 — DOC-04 Electronic Monitoring Notice approved and issued (GOV-108); daily run missed 11-27

Owner decisions on the review questions (2026-11-27): drivers get the notice (Q1); joint CISO and VP People approval to look at one person's activity (Q2); no company phones, drivers use only the app (Q3); one combined acknowledgment with the 12-09 drive (Q4). Owner: "Go ahead with all."

### Done
- **[DOC-04 Electronic Monitoring Notice](https://empire-city-taxi.atlassian.net/wiki/spaces/ECTG/pages/1015833)** (Confluence 1015833):
  - drafted 11-27 (v0.1);
  - reviewed by Michael Tran (comment 1015874) and Victor Hale (1114137);
  - **approved at v1.0 by Robert Feld, General Counsel** (950309) *[Simulated]*, dated 2026-11-28, next review 2027-11-28.
- **What the notice says:**
  - It uses the wording of NY Civil Rights Law §52-c(2)(b) unchanged.
  - It lists what ECT monitors, in two parts: everyone with an account, and drivers in the ECT Driver app.
  - It says what ECT doesn't do.
  - It sets out who receives it: new hires, a one-time catch-up for current staff, contractors and every driver.
  - Posting is online and on paper. Notice changes come before new monitoring.
  - Looking at one person's activity needs the joint approval of the CISO and the VP People.
  - Penalties: up to $500, then $1,000, then $3,000 per offense.
- **Policy Register** (Confluence 65685 v19): DOC-04 row and change log. DOC-03 stays reserved for the Vendor Inventory (GOV-154).
- **Announcement** [blog 950312](https://empire-city-taxi.atlassian.net/wiki/spaces/ECTG/blog/2026/11/28/950312), an email from Simone Laurent:
  - staff leave one comment by 2026-12-09, covering DOC-04 and the 11-25 policies;
  - drivers acknowledge in the app.
- **ECTG home page** (v6): a notice panel links to DOC-04, which is the online posting §52-c requires.
- **This PR:**
  - DOC-04 row in the `policy_register` seed.
  - A `policy_ack_deadlines` row (blog 950312).
  - `fct_policy_acknowledgments` now includes DOC-04 as well as the policies.
  - **DOC-04's due date is 2026-12-14** under the 10-business-day rule. An announced deadline can only move a due date later, so the post's 12-09 is a request, not the formal due date.

### Found
- **No daily run on 2026-11-27**, and as of 11:24 UTC on 11-28, no 05:17 UTC run either. GitHub never started the schedule.
  - The Google-side watchdog caught it: SEV4 at 17:06 UTC on 11-27, "the daily run has not completed by 12:00 New York".
  - The last run was 2026-11-26 (data loaded; it failed on purpose at the security-review step, GOV-169).
  - This is a missed POL-09 statement 18 deadline and needs a Jira record (GOV-123 evidence).
- **`policy_ack_deadlines` isn't in BigQuery yet:** it was added in PR #15, after the last run. It loads at the next run.

### Open / next
- Owner: start the daily run by hand (GitHub → Actions → Daily data refresh → Run workflow). `ect-daily` catches up the missing days.
- People team: put up the printed copies and photograph them (simulated evidence).
- **GOV-108** closes after this PR merges. **GOV-143** (F31) stays open for audit validation.
- **POL-05 next revision:** add the one-person monitoring rule (DOC-04 section 5.4).

---

## 2026-11-27 — Held items decided: generator tag pushed, daily run moved to 05:17 UTC; risk epic proposed

Owner decisions today ("I agree with everything else"):

### Done
- **Tag `generator-v0.4.0` pushed** (owner OK; GOV-157). It's on `022eeab`, the PR #10 merge.
  - Every `raw` batch is at 0.4.0 (checked: `hris_employees`, all 1,060 rows), since the 0.4.0 rebuild replaced older versions. So one tag covers everything a POL-15 rebuild needs.
  - No generator code has changed since `022eeab`: only `record.py`, `security_review.py` and `watchdog.py`.
  - **Release step added to CLAUDE.md:** after a version-bump PR merges, tag its merge commit (owner OK each time).
- **Daily run moved from 10:30 UTC to 05:17 UTC** (00:17 New York, 01:17 in summer). This PR; GOV-123.
  - **Why:** GitHub started the scheduled run at 20:02 UTC on 11-25 and 19:45 UTC on 11-26, about 9.5 hours late and after the 12:00 deadline (POL-09 s18). From 05:17, the same delay still finishes by about 10:00 New York. The off-the-hour minute avoids GitHub's busiest start times.
  - **Safe for the dates:** 05:17 UTC is always after New York midnight, and GitHub only starts late, never early. The generator's "yesterday" (New York) is a complete day. The security review's "yesterday" (UTC) ended 5 hours before.

### Decided (no change now)
- **GOV-148** (card expiry and cardholder name stored) stays held. It's planted scenario S03 and goes to the January council (CFO decides).
- **BigQuery policy tags** wait for GOV-148: the only Secret columns are those two.

### Risk register in Jira
- **Story GOV-172 "Risk Register (POL-06)"** holds R-002 to R-006 (GOV-149 to 153) as subtasks. The owner chose a Story over the proposed Epic and converted the five Tasks to subtasks in the Jira UI (2026-11-27). New risks are created there.

### Open / next
- **Watch the first runs at the new time** (from 2026-11-28). Then the Google watchdog should stop alerting on late runs. Add the start times to GOV-123.

---

## 2026-11-27 — Google-side watchdog live and tested end to end (GOV-170 Done); catalog baseline confirmed

### Done
- **PR #19 merged** (owner).
- **SQL updated** in both schedules and the test query (owner). Checked read-only: each matches the repo file exactly, and the account and settings are unchanged.
- **Log alert "ECT Watchdog Failed" created** (owner, setup J3). Google showed "Error 500" on save, but the alert was created: Monitoring's audit log shows a failed create at 10:30:11 and a successful one at 10:30:33, and only one alert exists.
  - Settings, checked read-only: filter `resource.type="bigquery_dts_config" severity>=ERROR`; 5-minute notification limit; 1-day autoclose; email channel "Maintainer Email".
- **J4 test:**
  - **First run, 10:32 UTC:** failed with SEV4 as intended, but no alert. It ran 2 minutes after the alert was created, before the alert was active.
  - **Second run, 10:50:34 UTC:** failed with SEV4. **The alert opened at 10:51:07** and the owner received the email.
  - The TEST query was then deleted (owner). Only the 16:05 and 17:05 queries remain.
- **Jira:**
  - GOV-170: closing comment, moved to **Done**.
  - Treatment evidence added to GOV-123 (finding F11) and GOV-150 (R-003). Both stay open for the audit and the exception review.
- **Catalog baseline (GOV-166):**
  - The owner found `stg_fleet_drivers` in Knowledge Catalog, with its description, name and type.
  - Checked read-only: it has all 10 labels and 0 of 17 column descriptions.
  - GOV-166 stays In Progress until Knowledge Catalog is added to DOC-02 (after the 12-01 council).
- **12-01 council:** the owner chose a *[Simulated]* meeting:
  - mostly positive, with 1 or 2 people apprehensive;
  - a data-owner conflict played up;
  - one dispute decided by vote.

  The details were kept from the owner at their request. It will be recorded on 12-01, not before, since simulations are dated the day they're recorded.

### Lesson
- **Test permissions as the account that will use them.** My read-only tests ran as the maintainer, who has full access, so the `ect-watchdog` permission gap only showed up when the query ran as that account.

### Open / next
- **Today:** the real checks run at 16:05 and 17:05 UTC. If the daily run is late again, 17:05 (12:05 New York) fails and alerts. That's correct, and it gets a Jira record (POL-09 s18).
- **Later:** decide whether to move the daily run earlier (GOV-123).

---

## 2026-11-27 — Watchdog email test (GOV-170): two defects found; SQL fixed and a log alert added

### Done
- **J2 verified:** `ECT Watchdog - 17:05 UTC` is in US, every day at 17:05 UTC, runs as `ect-watchdog`, with no destination table and the failure email on. The owner's first copy, named "ETC Watchdog - 17:05 UTC", was deleted.
- **Email test:** the test copy (On-demand, as `ect-watchdog`) was run at 10:11 UTC and failed. It found two defects.

### Defect 1: the watchdog couldn't read what it checks
- **Error:** "Access Denied: Table `marts.__TABLES__`".
- **Cause:** the legacy `__TABLES__` view needs permission to read table data (`bigquery.tables.getData`), which BigQuery Metadata Viewer doesn't include. The `raw` check passed because it uses `INFORMATION_SCHEMA`.
- **Why testing missed it:** my read-only tests ran as the maintainer's account, which has full access, so they couldn't catch a permission gap.
- **Impact if it had gone live:** both checks would fail every day with Access Denied. That means daily false alarms, and the run never actually checked.
- **Fix (owner approved):** `marts.INFORMATION_SCHEMA.PARTITIONS` joined to `INFORMATION_SCHEMA.TABLES` (base tables): the oldest of each table's latest change.
  - Same result as before (2026-11-26), covering all 21 base tables.
  - No new access: `ect-watchdog` still can't read data.
  - Applied to both `watchdog_check.sql` and the test copy.
  - Tested read-only: the test copy fails with "ECT WATCHDOG SEV4 … raw through 2026-11-25 (expected 2026-11-26); marts rebuilt 2026-11-26 (expected 2026-11-27)", and the real query says "Skipped" at 05:xx.

### Defect 2: the failure email doesn't reach a person
- **What happened:** no email arrived for the failed run (owner). This confirms Google's warning: the email goes to the account the query runs as.
- **Fix:** the fallback planned in the design, a **Cloud Monitoring log alert** on `resource.type="bigquery_dts_config" severity>=ERROR`, emailing the maintainer. It's new setup part J3, made by the owner in the UI; the email address stays in Google Cloud, never in the repo.
  - The failed run wrote an ERROR entry with the full error text (checked read-only), so the alert can match it.
  - Any scheduled-query error alerts. The only scheduled queries are the watchdogs, so a broken watchdog alerts too, as defect 1 would have.
  - Cost: free until at least September 2027, then about $0.35 a month.
- **Setup guide part J rewritten:**
  - J1: names, plus the warning that location is set from the query tab and can't be changed after saving;
  - J2;
  - **J3:** the log alert;
  - **J4:** the test, plus how to update the SQL in an existing schedule;
  - **J5:** what to do when it fires.
- README updated.

### Risks
- **Until the owner updates the SQL** in both schedules, today's 16:05 UTC run (11:05 New York) skips and the 17:05 run (12:05 New York) fails with Access Denied. It's harmless, and with no log alert yet, nobody is emailed.

### Open / next
- **Owner:**
  1. edit both schedules with the new SQL;
  2. set up J3;
  3. update the test query's SQL and run it again (J4), and confirm the alert email arrives;
  4. delete the test query.
- Then GOV-170, GOV-123 and R-003 get the evidence.

---

## 2026-11-27 — STD-02 v0.3: dataset-level metadata added (owner request)

### Done
- **Owner request:** STD-02 section 6 ("Metadata ECT keeps") only covered the table, column and glossary levels. It now covers datasets too.
- **STD-02 DRAFT v0.3** (Confluence 786433, page version 4):
  - **Section 6:** new "Dataset level" part. It lists the description, the five dataset labels (`layer`, `classification`, `data_custodian`, `environment`, `managed_by`), location, retention settings and access (shown only, decided under POL-02), and who changes each. **BigQuery stays the source of truth** for these; Option B covers only column classifications and glossary terms.
  - **Section 7a:** the monthly review pack now lists new datasets and changes to a dataset's description, labels or retention settings.
  - **Section 8.2:** new checks for datasets missing a description or a required label.
  - **D2:** dataset-level details added for the council.
  - A change-history row was added.
- **Policy Register v18:** STD-02 is at 0.3, with a change-log line. `policy_register.csv` matches.
- **Agenda (1015810, v3):** item 4.2 has a "Dataset level" row, and the post-meeting revision is now called v0.4.
- **Checked read-only (`bq show`):** all three datasets have a description and all five labels. Location is US, no default expiry is set, and time travel is 168 hours.

### Findings (left as found)
- **Out-of-date description:** the `marts` description still says the dataset is for "governance review (Collate)", but Collate was dropped on 2026-11-25. It's in the review pack for the council.
- **Proposals in v0.3 for the council to confirm:**
  - a change to the dataset `classification` label needs the CDO's and the CISO's approval;
  - a change to retention settings needs the General Counsel's agreement (POL-13).

---

## 2026-11-27 — STD-02 added to the Policy Register; first council meeting prepared (12-01)

### Done
- **Watchdog J1 verified** (read-only, through the Data Transfer Service API and the audit log). The owner's first save was in `us-central1` at 14:05 UTC. It was deleted and recreated, and now:
  - its location is `US`;
  - it runs every day at 16:05 UTC;
  - it has no destination table;
  - the failure email is on;
  - it runs as `ect-watchdog` (shown in the audit entry for its creation).
- **Policy Register v17** (Confluence 65685): **STD-02 Data Catalog & Metadata Standard**, DRAFT v0.2, has been added.
  - Owner: CDO. Approver: the Data Governance Council. Jira: GOV-166.
  - A change-log line was added.
  - The repo extract `policy_register.csv` matches.
  - The new row is a draft, and `fct_policy_acknowledgments` reads only approved policies, so nothing downstream changes.
- **Numbering clash found:** GOV-80 had planned STD-02 and STD-03 for the Classification and Labeling standards. It's on the agenda (item 4.4); the proposal is STD-03 and STD-04.
- **Confluence:**
  - New parent page **Data Governance Council** (1048579): how the council meets, the standing agenda, and a list of meetings.
  - **2026-12-01 Council Meeting: Agenda and Review Pack** (1015810), covering:
    - attendance and quorum;
    - a 90-minute agenda;
    - the KPIs, measured read-only;
    - new High issues;
    - decisions: the charter and cadence, STD-02 D1 to D4 and how terms and classifications are updated, the 30 proposed classifications, and numbering;
    - new data sources and vendors;
    - exceptions;
    - any other business.
- **Owner decisions (2026-11-27), Jira GOV-171 (In Progress):**
  - The first meeting is Tuesday 12-01.
  - Meetings run 90 minutes, with a standing agenda that includes the catalog review, new data sources and new vendors.
  - The charter questions go to the council.

### KPIs as measured (read-only, 2026-11-27)
- **Owner and steward labels:** 63 of 63 tables.
- **Secret and Confidential columns correctly classified:** 46 of 60 (77%). That leaves 13 approved under-classifications and 1 proposed.
- **Column descriptions:** 12 of 703 (2%: raw 0, staging 0, marts 12). `persist_docs` is on, but the models have almost no column descriptions yet. This was already in the backlog.
- **Planted DQ defects:** 100% caught.
- **Acknowledgments:** 6 of 7,905 done; due 12-09.

### Findings (left as found, for the council and the audit)
- **Agenda notice:** charter section 4 wants the agenda 3 business days ahead. Sent on 11-27, it has 2 full business days. This is recorded on the page as a deviation. In chat I had said today would work, which is wrong on a strict reading.
- **The charter conflicts with STD-01:**
  - it is still DRAFT v0.1 in the repo;
  - it puts minutes in the repo, while STD-01 says governance documents live in Confluence;
  - it says 60 minutes.

  All three are proposed as amendments, which need a two-thirds vote.
- **The issue register and decision log don't exist yet.** GV-001 to GV-007 are listed only in the charter.
- **`stg_fleet_drivers.ssn_last4` is proposed as Sensitive,** while it is Confidential in every other table.
- **The charter's "DQ pass rate" KPI is undefined** for warning rules that count failing records.

### Open / next
- **Owner:** merge PR #16, then this PR. Watchdog J2 and J3.
- **After 12-01:**
  - minutes on page 1015810, with decisions as `GV-D-###`;
  - STD-02 v0.3;
  - the charter to Confluence;
  - the classification register updates, through a PR.

---

## 2026-11-27 — Google-side watchdog designed (R-003, GOV-123); `ect-watchdog` created

### Done
- **PR #15 merged** (owner): the review case fix and the 12-09 deadline.
- **Backup alert, Option A (owner):** a BigQuery scheduled query on **Google's** scheduler, not GitHub's.
  - **What it checks:** at 12:05 New York, that `raw.app_trips` has yesterday's partition and that every `marts` table was rebuilt today. Metadata only.
  - **How it alerts:** if either check fails, the query fails on purpose with "ECT WATCHDOG SEV4", or SEV3 after 2 missed days. BigQuery then sends a failure email.
  - **Daylight saving:** two schedules (16:05 and 17:05 UTC), each checking only at 12:xx New York.
  - **Cost:** about $0 (roughly 600 MB of query a month, inside the free tier).
  - **Option not chosen:** Cloud Monitoring log alert. It can't express "by 12:00", only rolling absence windows, and it will cost about $0.35 a month from September 2027.
- **`ect-watchdog`** (owner, in the UI): BigQuery Job User plus Metadata Viewer, no key, and no sign-in grant (only Google's scheduler uses it).
  - **Why a new account and not `ect-monitor`** (owner asked): the security review alerts when anything but the workflow acts as `ect-monitor`, so Google's scheduler acting as it would raise a false alert every day. The backup also shouldn't depend on an account GitHub can use.
- **Tested read-only, all three paths:**
  - OK as of 11-26 (`raw` through 11-25, `marts` rebuilt 11-26);
  - ERROR as of 11-27 before the run;
  - "Skipped" outside 12:xx New York.
- **Files:**
  - `data-platform/sql/watchdog_check.sql`, plus a test copy `watchdog_check_TEST.sql` with the time check disabled;
  - setup guide part J (J1 to J4);
  - README.
  - The review now names `ect-watchdog` and `ect-catalog` instead of a generic service-account label.

### Risks
- **The alert email may not arrive.** Google warns that when a scheduled query runs as a service account, the failure email "might not" reach the person who set it up. Test J3 checks this. The fallback is a log-based alert email.
- **It may fire often.** With GitHub starting the daily run 9 to 10 hours late, the noon check will fail on those days. That's correct under POL-09 statement 18. Moving the daily run earlier (for example 01:17 New York) is a separate decision, after a few days of data.
- **It checks `marts`, not the GitHub run record,** because Google can't see GitHub. The record is committed minutes after dbt finishes.

### Open / next
- **Owner:** set up J1 and J2, then test J3. Then the Jira ticket (draft awaiting approval) and the GOV-123 and R-003 updates.

---

## 2026-11-27 — Second and third live reviews triaged (GOV-169): review bug fixed, late schedules recorded; acknowledgment deadline set to 12-09 (GOV-107)

### Done
- **Runs since the monitoring went live:**
  - 11-25 15:05 New York, scheduled: reviewed no days (11-24 was already done), 0 alerts.
  - 11-26 14:47 New York, scheduled: reviewed 11-25, 5 alerts, and failed at the last step as designed.
  - Watchdog on 11-26: one run skipped (the summer schedule) and one reported OK.
- **Triage, GOV-169** (owner approved; linked to GOV-150, GOV-122 and GOV-123). All 9 changes on 11-25 were expected setup work: the `scratch` rebuild grant, the 400-day retention, the Data Access settings, O6, and the `ect-catalog` roles and fixes. Two control issues were found.
  1. **The review missed 4 service-account permission changes.** These were sign-in grants on `ect-monitor` and `ect-catalog`. The IAM service logs them as `SetIAMPolicy`, but the check matched `SetIamPolicy` case-sensitively.
     - **Fixed** (owner approved): every method check is now case-insensitive, and a test was added.
     - The miss is recorded as evidence on GOV-122.
  2. **GitHub's scheduler ran 7 to 10 hours late.**
     - The daily run is set for 05:30 New York. It started at 15:05 on 11-25 and 14:47 on 11-26, so both runs finished after the 12:00 deadline (POL-09 statement 18).
     - The watchdog is set for 12:05. It ran at 19:29 and 19:59, so it didn't detect the late runs.
     - Recorded on GOV-123 and R-003 (GOV-150). The backup-alert cost check moves forward. **Not fixed** (findings rule).
- **Acknowledgment deadline (GOV-107), owner decision: 12-09**, the date staff were told.
  - New seed `policy_ack_deadlines` holds the announced deadline per policy major version (blog 459089: POL-01 to POL-15, due 2026-12-09).
  - `fct_policy_acknowledgments` uses the **later** of that deadline and the 10-business-day rule, so an announcement can extend a deadline but never shorten it. New hires still get 10 business days from their hire date.
  - The first post's Dec 8 rows in `policy_acknowledgments` (29 rows: STD-01 and the v1.0 approver acknowledgments) moved to Dec 9, as the announcement said.
  - **Checked read-only:** the compiled model, run with the new seed supplied inline, gives due date 2026-12-09 for all 15 policies and all 527 active staff. Not built locally, because the daily run would revert an unmerged build.
- **Tests:** `uv run pytest` gives 30 passed. `dbt compile` succeeds.

### Note
- For POL-01, 05, 06, 07 and 08 (approved 2026-11-24), 12-09 is one business day later than POL-01's 10-business-day rule. That's a lenient deviation, made because staff were told 12-09. Raise it at the first council meeting, or note it on GOV-107.

### Open / next
- Owner merges this PR. The next daily run then builds the new seed and model, and the review uses the fix.
- **Backup-alert price check** (R-003). The council cadence ticket is still to approve. The STD-02 Policy Register row is still to do.

---

## 2026-11-25 (afternoon) — Catalog: Collate dropped, Knowledge Catalog chosen; STD-02 drafted; `ect-catalog` created; lineage trial started

### Done
- **Collate dropped.** The free tier is a wait list that needs a company email, and connecting needs a service account key, which POL-02 statement 14 bans. Hosted alternatives were checked: DataHub Cloud, Secoda, Select Star and data.world have no confirmed free tier. Self-hosted OpenMetadata needs at least 6 GB of memory and 4 processors, too much for the laptop.
- **Knowledge Catalog chosen** (owner) over OpenMetadata on a Google Cloud machine (about $5 to $6 a month at 20 hours of use; about $98 a month if left on).
  - Free at ECT's size: search, automatic BigQuery metadata, glossary, aspects and policy tags.
  - Paid: lineage, quality scans and profiling.
  - The API was already enabled.
- **STD-02 Data Catalog & Metadata Standard**, DRAFT v0.2 (Confluence 786433).
  - Owner: the CDO. Approver: the Data Governance Council.
  - **D1, owner's direction: Option B.** The catalog becomes the source of truth after a one-time import, and the repository and BigQuery hold daily extracts. Section 7.6 adds checks to make up for the missing approval step. Section 7a adds a **monthly catalog review** at the council meeting, with yearly re-confirmation of terms and Secret/Confidential classifications.
  - **Open for the council:** D2 (aspect fields and values, including the planted `Restricted` rows and 29 data categories), D3 (who may edit), D4 (Looker Studio tables). The owner wants these discussed at the first council meeting.
- **`ect-catalog`** (owner, in the UI): Dataplex Catalog Editor plus BigQuery Metadata Viewer, keyless sign-in from this repository, no key.
  - Two mistakes were found by a read-only check and fixed by the owner: the old Data Catalog Editor role, and a repository value with a trailing period.
  - Google's docs don't say whether writing aspects to BigQuery entries needs a BigQuery permission. Test first; don't grant Data Owner.
- **Lineage API enabled** (owner) for a one-week cost trial. Check on or after 2026-12-02 (GOV-168).
- **Jira:**
  - GOV-166 (decision and baseline, In Progress).
  - GOV-167 (import and daily extract; waits on D2 and D3).
  - GOV-168 (lineage trial, In Progress).
- **Council cadence ticket drafted, not created yet.** It expands the charter's monthly first-Tuesday meeting to 90 minutes with a standing agenda: the catalog review, new data, new vendors, risks and exceptions, the security summary, and policy reviews. Still open: the first meeting date (12-01 or 01-05), and whether to move the charter (still a DRAFT in the repository) to Confluence under STD-01.

---

## 2026-11-25 — O6 done; PR #13 merged; first security review ran and was triaged (GOV-165)

### Done
- **O6 (owner, in the UI):** created `ect-monitor` (Private Logs Viewer only, no key); allowed keyless sign-in from this repo only (pool `github`); added the GitHub variable `GCP_MONITOR_SERVICE_ACCOUNT` and the secret `ECT_MAINTAINER_PRINCIPAL`. Claude checked parts 1 to 3 read-only; GitHub only shows a secret's name.
- **PR #13 merged** (`f2d8137`).
- **First run** (manual, 45677583945): every step passed except the final check, which failed as designed. Record `data-platform/run-records/2026-11-25_1342.md`.
  - **Correction:** the previous entry said this run would review 2026-11-25 (4 alerts). It reviewed **2026-11-24** (the UTC day before) and raised **7** "IAM policy changed" alerts. The 2026-11-25 alerts come in the 2026-11-26 review.
  - No access check (ACC) alerts: all nine known findings were unchanged, so the "new or increased only" rule worked.
- **Triage, GOV-165** (subtask of GOV-90, linked to GOV-150, GOV-122 and GOV-123; closed with a closing comment):
  - Dataset setup, the `ect-pipeline` grants and the role account grants were expected.
  - The `raw` read grants to `ect-role-analyst` and `ect-role-steward` (SEV2 under Appendix A) were **confirmed by the owner as deliberate planted audit material**, tracked as ACC-08, and not remediated.
- **Evidence comments** on GOV-150 (R-003 treatment status), GOV-122 (F10) and GOV-123 (F11). The findings and the exception stay open until the controls have run on a regular basis.

### Open / next
- **2026-11-26:**
  - The review covers 2026-11-25 (`scratch` sharing, Data Access settings, `_Default` retention, the O6 changes). Triage them in a new ticket.
  - The first scheduled watchdog check runs at 12:05 New York.
- **Possible improvement:** show the granted account and role in the run record, so triage doesn't need a log lookup.

---

## 2026-11-25 — Step 6: daily security review and watchdog built (J4); log reader setup steps written (O6)

Owner: "Let's do the monitoring code and hold off on setting up Cloud Storage."

### Done
- **Earlier question, export storage (GOV-158):** Cloud Storage, not a BigQuery dataset. Restoring needs the original zip, and the attachments are binary files. Setting it up is **on hold** (owner).
- **`ect-security-review`** (`src/ect_platform/security_review.py`, POL-09 statement 15 and Appendix A).
  - **What it reads:** every UTC day since the last review (normally yesterday; it catches up to 7 days after missed runs). It uses the Cloud Logging API, not BigQuery, so there's no query cost. It runs four filtered reads per day.
  - **The alerts it raises:**
    - IAM policy changes on the project or a dataset;
    - service account keys created;
    - logging changes (bucket, sinks, exclusions, Data Access settings);
    - `raw` read by an identity whose role has no `raw` row in `access_policy.csv`;
    - 5 or more denials for one identity within a sliding hour;
    - token exchanges not from this repo's workflow on `main`, and anyone but that workflow impersonating `ect-pipeline` or `ect-monitor`;
    - access check (ACC) findings that are new or higher than in the previous run record.
  - **Not covered yet:** the break-glass alert waits for GOV-89.
  - **Output:** writes `output/security_review.json`. `ect-record` adds a "Security review (POL-09)" section to the run record, which is the review record (statement 19). The last workflow step (`--check`) fails the run after the record is committed, so the evidence is kept and GitHub emails the maintainer.
- **Watchdog** (`src/ect_platform/watchdog.py`, `.github/workflows/watchdog.yml`, statement 18).
  - Runs at 12:05 New York. Two crons (16:05 and 17:05 UTC) cover summer and winter time; the script ignores the one that doesn't apply.
  - Fails if today's run record is missing: SEV4, or SEV3 if yesterday's is missing too.
  - Standard library only, with no Google sign-in.
- **Daily workflow:**
  - A second keyless sign-in as **`ect-monitor`**. Its credentials go only to the review step (`export_environment_variables: false`).
  - The review step, then the final check step.
  - If the variable `GCP_MONITOR_SERVICE_ACCOUNT` isn't set, the review records `not_run` and the run fails at the last step, so a critical control that isn't running is never silent.
- **Privacy:** the repo is public. Identities show as `maintainer` (through the secret `ECT_MAINTAINER_PRINCIPAL`), our service account names, `github-workflow (main)`, `google-system-account` or `unknown-identity-<sha256 prefix>`. No emails or IP addresses ever appear.
- **Tests:** `tests/test_monitoring.py`, 12 new tests (every alert type, the sliding window, catch-up, record parsing, privacy, the watchdog in both seasons). `uv run pytest`: **28 passed**.
- **Run against real logs** (read-only, as the owner, locally, with `--day`):
  - **2026-11-24:** 7 alerts, all IAM and dataset-sharing changes by the maintainer during role-account setup.
  - **2026-11-25:** 4 alerts: `scratch` dataset sharing, Data Access settings and the `_Default` bucket retention change.
  - There were no false alerts on 434 + 153 `raw` reads (the pipeline and the maintainer are both approved), denials stayed under the threshold, and all sign-ins came from the workflow.
  - The result file contains no `@`.
- **Docs:** `docs/github-actions-setup.md` parts H (O6 owner steps) and I (watchdog); README commands and monitoring limits.
- **Correction:** the 2026-11-25 approvals entry said the `_Default` bucket keeps 365 days. It's **400** (the owner's setting; POL-09 statement 12). Fixed above and in the Jira comments on GOV-94 and GOV-121.

### Decisions (owner, 2026-11-25)
- **A separate log reader account (`ect-monitor`, Private Logs Viewer only)**, not the pipeline account, so the monitored identity can't read its own audit trail (POL-09 statement 8).
- **ACC findings alert only when new or increased** compared with the previous run record. Known findings are still listed in each record. This avoids a failed run and an email every day for the planted findings.
- **Google-side backup alert:** decided later, after checking Cloud Monitoring's alerting price. Meanwhile the watchdog shares the GitHub scheduler with the daily run (the 2026-11-25 schedule never fired), so a scheduler outage silences both. This is recorded on GOV-123.

### Known limits
- `UpdateDataset` entries can't show whether permissions changed (the log shows the whole dataset), so every dataset update counts as a possible permission change (SEV3). Console sharing produces both a `SetIamPolicy` and an `UpdateDataset` alert.
- Only Google Cloud logs are reviewed automatically. GitHub and Atlassian logs need the monthly manual review (statement 17, GOV-95).

### Open / next
- **Owner, O6 (before merging the PR):** setup steps H1 to H4 (create `ect-monitor` with Private Logs Viewer, grant the workflow impersonation, add the variable `GCP_MONITOR_SERVICE_ACCOUNT` and the secret `ECT_MAINTAINER_PRINCIPAL`). Then merge, then run H5.
- **The first run after setup will fail on purpose:** it reviews 2026-11-25, which has the 4 alerts above. These become the first triage records in Jira (POL-09 statement 15). The O6 changes then show in the next day's review.
- Then update GOV-122 (F10) and GOV-123 (F11) with evidence, and R-003 (GOV-150) with the treatment status. The findings stay open until the controls have run (findings rule).

---

## 2026-11-25 — Realism review applied; all 15 policies approved; Jira consolidated into three stories; combined announcement

Owner gave blanket approval for steps 1–5 ("Let's do 1-5. You have my blanket approval."). Not included: step 6 (J4 monitoring code and O6) and git tags (still need the owner's OK). All approvals, reviews and acknowledgments are *[Simulated]* and dated today.

### Done
- **Step 1: approved documents revised to match the real setup** (card numbers are no longer stored; no Cloud KMS, Secret Manager or CMEK). Each revision has an approver comment.
  - **Major versions:** new approval date 2026-11-25, next review 2027-11-25, staff re-acknowledge.
    - DOC-01 v2.0: card numbers are entered only into the providers' components and terminals; ECT keeps a token and the last 4 digits.
    - DOC-02 v2.0: data tiers per tool lowered.
    - POL-02 v2.0, POL-03 v2.0 (Secret data not allowed in the platform; removed promptly), POL-04 v2.0 (now about card entry: the in-app card form and terminal checks).
  - **Minor versions:** dates unchanged, earlier acknowledgments still count. POL-01 v1.2, POL-05 v1.1, POL-08 v1.2.
  - STD-01, POL-06 and POL-07 were checked and need no change.
  - **Repo:** `00-company/company-profile.md` no longer claims a working DR region (the real platform runs in BigQuery `US` and recovers by rebuilding). It also says cards are entered only into the providers' components. `system-description.md` changes 99.9% to 99.5% uptime and corrects the data line.
- **Steps 2 and 5: POL-09 to POL-15 revised and approved at v1.0.** Each page got one write carrying both the realism changes and the approval, plus an approver comment:

  | Policy | Approver (comment) | Decisions | High gap and exception |
  |---|---|---|---|
  | POL-09 | CISO (557467) | `_Default` bucket, 400 days (corrected from "365" on 2026-11-25) | R-003 (GOV-150): alerting and daily review, to 2027-01-31 |
  | POL-10 | CISO (557469) | (c): ASV scans and pen tests not applicable | none |
  | POL-11 | CISO (491857) | A1, B1, C1 | none |
  | POL-12 | CISO (557471) | A1 (DOC-03), B1; Google and GitHub are no longer PCI service providers | R-004 (GOV-151): vendor programme, to 2027-02-28 |
  | POL-13 | General Counsel (491872) | Option 1: logged deletes, disposal log, rebuild filter; legal minimums confirmed | none |
  | POL-14 | VP People (557473) | 1(a), 2(b), 3(c) | R-005 (GOV-152): training, to 2027-01-31 |
  | POL-15 | VP Operations (426584) | Real vs simulated targets; no DR region; rebuild test in `scratch` | R-006 (GOV-153): untested recovery, to 2027-02-28 |

  - **Policy Register** (page 65685, v16) shows all 15 policies APPROVED, with a change-log row.
  - **`policy_register.csv` seed** updated to match, for all rows changed today.
- **Risk register:** R-002 to R-006 created as GOV-149 to GOV-153 and linked to their findings. R-001 (GOV-93) closed as treated, by removal: residual time-travel and fail-safe copies end about 2026-12-09.
- **Step 3: tickets.**
  - **Closed, each with a closing comment:**
    - Approval subtasks GOV-63 to GOV-69.
    - Decisions GOV-96, 97, 98, 100, 101, 102, 104; alignment items GOV-105 and 106.
    - GOV-71, GOV-124 (F12, Dependabot on), GOV-129 (F17), GOV-131 (F19).
  - **GOV-94** (log lock): in progress, decision due 2026-12-31.
  - **GOV-127** (F15): re-rated from High to Medium, with summary and description rewritten.
  - **Update comments:** GOV-72, 73, 74, 110, 116, 121, 122, 123, 128, 139, 141, 142.
  - **New subtasks under GOV-90:**
    - GOV-154 DOC-03 Vendor Inventory
    - GOV-155 cryptography inventory
    - GOV-156 terminal list, inspections and payment-page script inventory
    - GOV-157 generator tags (held for owner OK)
    - GOV-158 quarterly Jira and Confluence export (owner)
    - GOV-159 `ect-config-check`
    - GOV-160 build-tools manifest
    - GOV-161 driver check and training seed
    - GOV-162 disposal log and rebuild filter
    - GOV-163 rebuild runbook and first restore test
    - GOV-164 legal-hold and deletion-request logs, BIA, BC/DR plan, tabletop
- **Step 4: three stories.** The API could change subtask parents, so no Jira Move in the UI was needed.
  - **GOV-81 Draft Follow-ups:** GOV-75 to 80 and GOV-94 to 106.
  - **GOV-82 Audit Findings:** F1 to F7, GOV-71 to 74, and F9 to F35. GOV-148 related.
  - **GOV-90 Policies into Operation.**
  - The three stories were renamed and their descriptions rewritten.
  - **Closed with closing comments:** GOV-70, GOV-120, and the policy stories GOV-12 to 18 (no open subtasks left).
- **Step 5: combined announcement**, [blog 459089](https://empire-city-taxi.atlassian.net/wiki/spaces/ECTG/blog/2026/11/25/459089), an email from Victor Hale.
  - Covers the card-number change, the seven new policies, and which updates need re-acknowledgment: POL-02, 03 and 04.
  - **One deadline, 2026-12-09:** one comment covers POL-01 to POL-15 and replaces the first post's Dec 8 date. A footer comment on 491767 says so.
  - GOV-107 summary and comment updated.

### Decisions
- **One acknowledgment deadline (2026-12-09) instead of two.** It is 10 business days from today, counted the same way as the first post. Rationale: the owner asked for a single deadline, and the first deadline was only a day earlier.
- **Policy stories GOV-12 to 18 closed.** After consolidation, all remaining work is in the three stories, so these had nothing left.
- **F9 (GOV-121) stays High and is not excepted:** retention is now met, but the lock decision is due 2026-12-31.

### Open / next
- **Owner:** merge this PR. Then the O7 lock decision by 2026-12-31 (GOV-94), and the first export (GOV-158) by 2026-12-31.
- **Later:** step 6 (J4 monitoring and O6, the treatment for R-003, due before 2027-01-31); git tags (GOV-157, needs OK); simulated acknowledgments after the announcement; GOV-148.
- **Exception expiries:** R-003 and R-005 on 2027-01-31; R-004 and R-006 on 2027-02-28.
- **Known mismatch, to settle in GOV-107:** `fct_policy_acknowledgments` sets `due_on` as 10 business days from each approval date.
  - POL-02 to 04 and POL-09 to 15 are due 2026-12-09.
  - POL-01, 05, 06, 07 and 08 are still due 2026-12-08, one day before the announced single deadline.
  - Either add an announced-deadline override to the model, or treat 12-09 acknowledgments as on time in the follow-up.
  - Checked after `dbt build --select policy_register+`: PASS 17, ERROR 0.

---

## 2026-11-25 — Raw rebuilt with generator 0.4.0; full card numbers, SSNs and bank numbers gone; scheduled run missed

### Done
- **PR #10 merged** by the owner (022eeab).
- **GOV-148 (Bug)** created, owner-approved: `card_expiry` and `cardholder_name` are still stored in `payments_rider_cards` and are Secret under the standard (planted S03). Labels `audit-finding`, `bug`, `data-classification`; relates to GOV-82. Fixed in the data classification mapping work, not before.
- **Owner decisions on the follow-ups** (approved "everything else is fine"):
  - POL-03 v2.0 gets the rule "Secret data must not be stored in ECT's data platform; it stays with the provider; if found, it's a security incident and is removed within 5 business days". This goes in the same major revision as the "don't store the full value" change.
  - ECT does **not** receive card numbers and mask them on arrival. It would widen PCI scope, and real taxi apps and terminals send cards straight to the processor.
  - A planted card number in a free-text field is added later with the GOV-74 scan.
- **Test rebuild in `scratch`:**
  - The four tables were loaded from the verified 0.4.0 batches and compared in BigQuery with `raw`: 6,984 rows.
  - 0 unmatched rows, 0 differences in unchanged columns, 0 wrong last-4 values or defect codes.
  - The test tables were deleted afterwards.
- **Rebuild of `raw` (owner approval O5, "Yes")** at 2026-11-25 13:14 UTC:
  - Tables: `hris_employees` (1,058 rows), `fleet_drivers` (693), `payments_rider_cards` (3,905), `gov_planted_defects` (1,328). Same counts as before; all rows `_generator_version` 0.4.0.
  - Each table was deleted and recreated from the 0.4.0 batches, Jan 1 to Nov 23, with load label `component: ect-rebuild-040`.
  - Table labels: `hris_employees` and `fleet_drivers` → confidential.
  - **Old values:** restorable through BigQuery time travel until **2026-12-02 13:14 UTC**. After that they're in Google's fail-safe until about **2026-12-09**, then gone.
- **`dbt build`:** PASS 134, WARN 39, ERROR 0.
  - DQ-04, 07, 13 and 16 catch exactly the same counts as before: 20, 114, 14 and 15.
  - CLS-03 +27: the proposed register rows.
  - CLS-01 188: none on the new columns. 32 are the policy register and acknowledgment tables from PR #8, which the last run record predates.
- **A miss in PR #10, fixed here:** the people and driver staging views (`stg_hris_employees`, `stg_fleet_drivers` and their history views) still carried `classification: secret`, so CLS-04 rose from 18 to 28. `_staging.yml` is now `confidential`, giving CLS-04 = 24. The live views already carry the new label, built from this branch. **Merge this PR before the next daily run**, or that run puts the old labels back (warnings only).
- **Laptop:** `data-platform/output/` deleted (213 MB, 327 days of 0.2.0 batches, the only local copy of the full card numbers). It was git-ignored and regenerable. The owner's laptop is portfolio tooling, outside ECT scope.

### Found
- **The scheduled daily run (05:30 New York) didn't happen on 2026-11-25, and nothing alerted anyone.** The workflow is active, the cron is valid and it's on `main`. GitHub has never started a scheduled run of it: the only runs are three manual ones on 2026-11-24. `raw` therefore ended at Nov 23.
  - Evidence for **F11 (GOV-123, no missed-run alert)**. Not fixed (findings rule); the fix is the J4 watchdog.
  - The next run catches up Nov 24 and 25 with 0.4.0. It will also show whether the new IAM and STS audit logs capture the pipeline's sign-in.

### Open / next
- Owner: merge this PR, then trigger the daily run (Actions → Daily data refresh → Run workflow), or wait for tomorrow's schedule.
- Simulated owner approval of the 27 proposed register rows.
- Git tags for generator versions (owner OK pending).
- J4 to J8 as listed below.

---

## 2026-11-25 — Realism review decisions, owner settings, generator 0.4.0 (no full card, SSN or bank numbers)

### Done
- **Realism review of all policies** (POL-01 to POL-15, STD-01, DOC-01, DOC-02) against the real setup, under the owner's constraint of **no Cloud KMS, Secret Manager or CMEK**. Six read-only reviews. Result: every policy stays; statements that can't apply say "not applicable" with the reason; new settings cost under $0.10/month. Nothing in Confluence or Jira edited yet.
- **Owner settings (owner made them in the UI; Claude checked each read-only):**
  - GitHub: Dependabot alerts and security updates on (secret scanning and push protection were already on). Failed-workflow emails: owner confirmed (can't be read from here).
  - Cloud Logging: `_Default` bucket retention **30 → 400 days**. Not locked; Log Analytics off.
  - Data Access audit logs (Admin Read, Data Read, Data Write) on for **Security Token Service API** and **Identity and Access Management (IAM) API**. The page has no separate "IAM Service Account Credentials API" row; the IAM row is expected to cover the pipeline's token logs. To be confirmed in the logs after the next daily run.
  - BigQuery dataset **`scratch`** (US) created by the owner; `ect-pipeline` has write access. For the yearly rebuild test (POL-15) and the 0.4.0 rebuild test.
- **Generator 0.4.0** (branch `realism-decisions-generator-040`):
  - Cards: only `card_token` (processor token, letters only, from its own random stream keyed by `card_id`) and `card_last4`. SSNs: `ssn_last4`. Payout bank accounts: `payout_account_last4` plus `payout_account_token`. The full values are still drawn, so every other value keeps its random draws, but never output.
  - The four planted defects on those columns were redefined on the last-4 values, with the same rates and the same records: `driver_ssn_last4_short`, `driver_payout_last4_masked`, `card_last4_missing`, `employee_ssn_last4_masked`. DQ-04, 07, 13 and 16 follow.
  - HR fields for POL-14 on `hris_employees`: `screening_status`, `screening_date`, `confidentiality_agreed_on`. Corporate staff only; drivers are screened through the fleet background check. Clean values; no planted gaps yet (needs a steward-proposed DQ rule first).
  - Table labels: `hris_employees` and `fleet_drivers` Secret → Confidential. `payments_rider_cards` stays Secret / PCI: expiry and name are still Secret, and the PCI label changes with DOC-01 v2.0.
  - Classification register and answer key: 27 rows replaced or added, all **proposed** (owner approval pending). Planted scenario S06 carried over to `stg_fleet_drivers.ssn_last4` (Sensitive, should be Confidential); S03 and S11 untouched.
- **Verified:** `pytest` 16 passed (3 new tests). Full history regenerated with 0.4.0 (Jan 1 to Nov 23, 380,115 rows) and compared with the existing batches: **0 problems**. Every other table is identical, the same records carry the same planted defects, and every last-4 value matches. A scan of 6.2 million text values found no SSN-shaped values and no card numbers.

### Decisions (owner, 2026-11-25: "Let's go with all of your recommendations")
- **Don't store full card numbers, SSNs or bank account numbers**: last 4 plus provider tokens (POL-11 B1, GOV-97 A1/B1/C1). This is how POL-04's "card number unreadable" is met without key products.
- **One-time exception to "raw is append-only"**: after the owner sees the 0.4.0 rebuild test, `hris_employees`, `fleet_drivers`, `payments_rider_cards` and `gov_planted_defects` are rebuilt in `raw` from 0.4.0 batches, and the local `output/` batches with full card numbers are deleted. It's recorded here as the decision of record (there's no `GV-D` log yet). BigQuery keeps the old values for about 14 more days (7 days time travel plus 7 days fail-safe); that end date gets recorded at the rebuild.
- **POL-09 logs:** keep 12 months in the existing `_Default` bucket (owner: "if we have the `_Default` bucket, we don't need the dataset"). No new bucket or log dataset. Locking the retention is decided after a 30-day trial, around Dec 28, and only if Google allows locking `_Default`.
- **POL-10:** internal and external (ASV) scans and penetration tests are **not applicable, with reasons**, not simulated (GOV-96 option c). Simulated reports about systems that don't exist would be false evidence.
- **POL-15:** real, tested recovery targets for the data platform; design targets checked by walk-throughs for the fictional services; no DR region (correct the company profile; uptime claim to 99.5%).
- **POL-14:** overdue training is reported and escalated (option b, simulated).
- **Revisions to approved policies now**, before the Dec 8 acknowledgment deadline, while only the approvers have acknowledged.
- **POL-05:** add the line that the portfolio's AI assistant is out of scope.
- **Enterprise baseline assumptions** (owner): all sign-ins use 2FA; all ECT laptops are centrally managed (auto-lock, automatic updates, disk encryption). **The owner's own laptop is portfolio tooling, not an ECT device**, like the AI assistant. It leaves DOC-01's in-scope systems; F16 and F27 become about assumed and simulated ECT devices.
- **Who does what:** setup tasks for the owner (O1 to O8) are separate from the work done as Jordan Ellis, Data Governance Manager (J1 to J8).

### Risks
- **Merge timing:** 0.4.0 changes the columns of three raw tables. If it's merged and the daily run starts before the rebuild, that day's load fails. Merge it right after a daily run, then do the rebuild and a `dbt build` the same day.
- `raw.payments_rider_cards` will show a new CLS-04 finding (its Secret label above its highest registered column), because S03 under-classifies expiry and name. Expected; it clears with the DOC-01 v2.0 relabel.

### Found (for GOV-74, the card-number discovery scan)
- Numeric IDs pass the Luhn check by chance: `app_trips.trip_id` (13 digits) and `app_trips.tlc_source_key` (35,934 hits). The scan must skip known ID columns or it will flood with false alarms.

### Open / next
- PR for 0.4.0; owner merges after a daily run. Then J3: test rebuild in `scratch`, owner says yes (O5), rebuild `raw`, run `dbt build`, delete `output/`, record the time-travel end date.
- Git tags for each generator version (proposed: `generator-v0.2.0` on 603c24f, `generator-v0.3.0` on f63ac4b, `generator-v0.4.0` on the merge). They need the owner's OK, because tags are pushed to GitHub outside a PR.
- Simulated owner approval of the 27 proposed register rows (vp-people, vp-driver-operations, cfo).
- J4 monitoring code; J5 document revisions; J6 ticket updates and drafts; J7 Jira consolidation; J8 approvals.

---

## 2026-11-24 — 53 follow-up, finding and operation tickets created; first policy announcement

### Done
- **Owner approved all drafts** ("we'll revisit what needs to be updated and what can actually be actioned at another time"). Created in GOV, all To Do:
  - **Draft follow-ups GOV-94 to GOV-106:** 11 under the policy stories GOV-12 to GOV-18, 2 alignment items under GOV-81 (GOV-105 POL-01 st. 6 / POL-05 5.11; GOV-106 POL-03 vs POL-11). Owner-decision tickets block the approval sub-tasks: GOV-94→63, GOV-96→64, GOV-97→65, GOV-98→66, GOV-100 and GOV-101→67, GOV-102→68, GOV-104→69.
  - **Audit findings:** story **GOV-120** (label `audit-finding`, relates to GOV-82) with **F9 to F35 = GOV-121 to GOV-147**: 9 High, 13 Medium, 5 Low. Not fixed (owner rule).
  - **Operation tasks GOV-107 to GOV-119** under GOV-90 for the approved policies. GOV sub-tasks have no due-date field, so first due dates are in the summaries.
  - Comments: GOV-66 (cross-references to update when POL-12 is published), GOV-15 (confirm the in-cab payment path).
- **Quarterly checks follow the calendar quarter** (owner): first access review, risk register review, change sample and card-data checks due **Mar 31, 2027** (GOV-113 to GOV-116).
- **First policy announcement**, a Confluence blog post written as an email to staff (blog 491767, *[Simulated]*): POL-01 to POL-08 plus STD-01, DOC-01, DOC-02; read and acknowledge by Dec 8 by commenting on the post. Linked on GOV-107.

### Decisions
- **Announcements** (owner, replacing the earlier "no announcement post", which the owner called short-sighted): every policy approval or change gets a blog post written as an email, within 10 business days (STD-01 s11 already requires announcing and doesn't say how, so STD-01 is unchanged). Recorded in `CLAUDE.md` #5 and memory.
- Blogs were off in ECTG; the owner switched them on in the space settings.

### Open / next
- Owner decisions on the 7 new policies (GOV-94, 96, 97, 98, 100/101, 102, 104), then approvals GOV-63 to GOV-69, each with its own announcement post.
- Operation items for POL-09 to POL-15 are held until each is approved (list in the ticket drafts, carried into each approval sub-task then).
- Staff acknowledgments now come as comments on the announcement post; the Dec 1 simulated batch should use those comments as evidence.

---

## 2026-11-24 — POL-09 to POL-15 drafted and reviewed to v0.9 (parallel)

### Done
- 7 parallel agents each drafted one policy from the approved template (Policies folder), ran its *[Simulated]* review (≥1 point accepted, ≥1 rejected with reason) and closed its draft and review sub-tasks with closing comments. Stories → In Progress. **Approval sub-tasks GOV-63 to GOV-69 untouched**, waiting for the owner.

  | ID | Page | Story | Statements | Owner decisions (PROPOSED) |
  |---|---|---|---|---|
  | POL-09 Logging & Monitoring | 557400 | GOV-12 | 22 | where 12-month audit logs live |
  | POL-10 Vulnerability & Patch | 458990 | GOV-13 | 18 | ASV scans / pen tests for simulated card systems |
  | POL-11 Encryption & Key Mgmt | 557358 | GOV-14 | 22 | card-number method, key type, SSN/bank deadline |
  | POL-12 Vendor & Third-Party Risk | 426423 | GOV-15 | 26 | inventory location, review frequency |
  | POL-13 Data Retention & Disposal | 491690 | GOV-16 | 18 | disposal when `raw` is append-only; GC confirms 4 periods |
  | POL-14 HR Security | 426362 | GOV-17 | 21 | screening scope, overdue training, training platform |
  | POL-15 BC/DR | 557298 | GOV-18 | 16 | RTO/RPO per service; build or drop the DR region |
- An 8th read-only agent listed what the approved policies (POL-01 to POL-08, STD-01, DOC-02) need to run that isn't ticketed.
- Register page v14 and `policy_register.csv`: POL-09 to POL-15 `in_review`, 0.9, page IDs.
- Read-only checks by the agents (no settings changed): Dependabot alerts off; `_Default` log bucket 30 days, unlocked; no alert policies; Cloud KMS not enabled (the `gcloud` prompt to enable it defaulted to No); datasets US multi-region, no expiry, no CMEK; 0 user-managed service-account keys. A local dependency scan was blocked by the permission check and not retried.

### Open
- **Ticket drafts for owner approval** (merged and de-duplicated across the 8 agents): 11 draft follow-ups under the policy stories (owner decisions block each approval sub-task) + 2 alignment items under GOV-81; 27 audit findings F9–F35 under a new findings story (9 High, 13 Medium, 5 Low); 13 operation sub-tasks under GOV-90 for the approved policies. Operation items for POL-09 to POL-15 held until each is approved.
- **Conflict to resolve:** STD-01 s11 requires announcing approved policies; the earlier owner decision was no announcement post (draft 3.1).

---

## 2026-11-24 — Correction: why PRs #5 and #7 missed commits

### Done
- **Root cause found (corrects earlier entries that blamed GitHub lag).** In both cases Claude pushed commits *after* the owner had merged the PR. A merged PR never picks up new commits, so they never reached `main`:
  - PR #5 merged 22:38:02 UTC; `e06e7d6` committed 22:38:57 (55 s later).
  - PR #7 merged 02:31:52 UTC; `236ba03` (02:34:31) and `13c0e5f` (02:39:51) came after.
  Claude's check counted commits but never looked at whether the PR was still open. The owner merged correctly both times.
- `236ba03` and `13c0e5f` carried to branch `policies-09-15` as `f7b8d79` and `63b2393`.
- `CLAUDE.md` #3 and memory: check the PR is still open before every push; no new commits to a PR once it's called ready; merge on the owner's go-ahead with `gh pr merge --match-head-commit`, which refuses if the PR doesn't hold that exact commit.

### Decisions
- **No local `pre-push` hook** (owner): a hook refusing pushes to a merged PR's branch was proposed and declined. The written rule (check the PR is open before every push) is the control; a missed commit stays on its branch and can be carried into the next PR.

---

## 2026-11-24 — Incident reports move to the Security Incidents (SI) Jira space

### Done
- Owner created Jira space **Security Incidents (SI)** (work types Task, Sub-task) for submitted incident reports, and renamed the GOV space **GRC Program** (shown in Jira as "GRC Program").
- *Report a Security Incident* (Confluence 426241) v2: Route A now says to create a Task in the SI space, no label needed, and not to use GOV; Route B says Security opens the SI ticket; change-history row added.
- Space home page v5: names GRC Program (GOV) and Security Incidents (SI).
- `CLAUDE.md`: both Jira spaces listed.

- **POL-01 v1.1** (CEO, comment 458963) and **POL-08 v1.1** (CISO, comment 458966), owner approved: statement 7 / the channel definition and statement 1 now point to the *Report a Security Incident* page instead of naming a Jira route, so future route changes only touch the how-to. Minor versions: staff acknowledgments of v1.0 still count (the model matches on major version). Register page v12 and CSV updated.
- *Report a Security Incident* moved into the **How-To's** folder (owner request); v3 change history notes the policy revisions.

### Decisions
- **SI space access isn't configured** (owner): ECT staff are fictional, so there's nobody to grant or restrict. Recorded as a simulation note on the how-to page; in a real company only the Security team would see reports.

---

## 2026-11-24 — All eight policies approved; DOC-02 tools list; all-staff acknowledgments; Claude creates PRs (POL-07 v1.1)

### Done
- **AI tools decision (owner):** all AI tools may receive **Public data only**; may be revisited if data is hashed, tokenized or encrypted first (CISO, after a POL-12 vendor check). **Scope note** (owner): the rule covers AI tools ECT would adopt or integrate (e.g. Gemini, ChatGPT); the assistant used to build and run this portfolio (Claude) is out of scope. It is portfolio tooling, and all ECT data is fictional. Recorded as a scope boundary, not an exception.
- **DOC-02 Approved Tools List** (Confluence 458876) approved v1.0 by the CISO (comment 557268) *[Simulated]*; GOV-76 Done. Added to the register as DOC-02.
- **POL-05 Acceptable Use Policy** approved v1.0: post-review change aligned 5.4.12/5.4.13 and the definitions with the AI decision; approved by Simone Laurent, VP People (EMP10049, 491653) and Victor Hale, CISO (557271). GOV-59 and GOV-8 Done. **All eight policies POL-01 to POL-08 are now approved.**
- **POL-07 v1.1** (minor change): under the small-team allowance, Claude creates each PR with its full description; the owner approves by merging. Approved by Arjun Mehta, VP Engineering (491656). Comment on finding GOV-83. CLAUDE.md #3 and memory updated. Owner chose option (a) after PRs #3, #5 and #6 opened with the blank template.
- **All-staff acknowledgments** (owner decision: all staff acknowledge every approved policy, drivers included):
  - new model `marts.fct_policy_acknowledgments`: one row per **active** employee per approved policy, derived daily from HR data, so new hires appear and leavers drop off.
  - due 10 business days after the later of approval and hire date (POL-01 statement 6, STD-01 section 11); weekends skipped, holidays not.
  - matches on the **major** version: minor revisions (POL-07 1.1) keep earlier acknowledgments.
  - the seed now records acknowledgments **received**; 10 approver rows added (their approval comments count).
  - today: 526 staff × 8 policies = 4,208 rows; 10 acknowledged, 4,198 pending, due Dec 8, 2026.
- **Register:** Confluence page v10 and `policy_register.csv`: POL-05 approved 1.0, POL-07 1.1, DOC-02 added.
- **Tickets (owner approved drafts):** story **GOV-90** "Put the approved policies into operation" with **GOV-91** first tabletop (May 2027, blocked by GOV-88) and **GOV-92** first annual risk assessment (Mar 31, 2027); **GOV-93** R-001 cardholder data stored readable (High, 15), standalone `risk-register` Task linked to GOV-90, GOV-86, GOV-70.

### Decisions
- R-001 is a standalone Task, not a sub-task: POL-06's register is a list of standalone `risk-register` Tasks reviewed quarterly.
- Acknowledgment list is derived, not hand-listed, because headcount changes daily.

### Open / next
- **POL-01 statement 6** names only POL-01 and POL-05 for acknowledgment; the owner's all-staff, all-policies decision goes further. Align at POL-01's next revision.
- The yearly re-acknowledgment isn't modelled yet (first due Nov 2027).
- Dec 1: record further simulated acknowledgments, leaving some overdue after Dec 8.
- POL-09 to POL-15 drafting.

---

## 2026-11-24 — Seven policies approved at v1.0; incident reporting channel; tools list drafted

### Done
- **GOV-75 Done:** new page *Report a Security Incident* (Confluence 426241, supporting document, owner CISO): Jira GOV ticket labelled `security-incident`, or tell the CISO directly. Linked from the space home page; named in POL-01 statement 7 and POL-08 statement 1 (post-review owner changes, accepted by each approver).
- **Approved at v1.0** *[Simulated]*, dated 2026-11-24, next review 2027-11-24. Each has an "Approved version 1.0" comment, an approved page (banner, version, dates, change history), and its approval sub-task and story closed with closing comments:

  | Policy | Approver (employee ID) | Comment | Tickets closed |
  |---|---|---|---|
  | POL-01 | Marcus Delgado, CEO (EMP10001) | 491625 | GOV-55, GOV-4 |
  | POL-02 | Victor Hale, CISO (EMP10013) | 557235 | GOV-56, GOV-5 |
  | POL-03 | Renée Okonkwo, CDO (EMP10002) | 557238 | GOV-57, GOV-6 |
  | POL-04 | Thomas Brennan, CFO (EMP10043), then CISO | 426293, 491630 | GOV-58, GOV-7 |
  | POL-06 | Victor Hale, CISO | 557232 | GOV-60, GOV-9 |
  | POL-07 | Arjun Mehta, VP Engineering (EMP10064) | 557245 | GOV-61, GOV-10 |
  | POL-08 | Victor Hale, CISO | 557241 | GOV-62, GOV-11 |

- **Policy Register** page v7 and `policy_register.csv` extract updated to `approved,1.0,2026-11-24,2027-11-24` for these seven.
- **GOV-76 In Review:** *Approved Tools List* v0.1 (Confluence 458876) drafted, owner CISO. The AI-tools section is PROPOSED with three options and waits for the owner's decision. POL-05 (GOV-59) stays at v0.9 until then.
- **PR template** now links the POL-07 page (GOV-61 step 4).
- Work ran in two waves of parallel agents: GOV-75 + POL-01 first (POL-01 must be approved before the policies under it), then POL-02/03/04/06/07/08 at once.
- **PR #5 gap:** it was merged before GitHub picked up its last commit (`e06e7d6`, the GOV-82 findings entry), so that entry never reached `main`. Carried into this branch as a cherry-pick.

### Decisions
- The "copy approved text to the repo" steps in the approval tickets were skipped: superseded by STD-01 v2.0 (Confluence only). Noted in each closing comment.
- No council decision-log (`GV-D-###`) entry for policy approvals (GOV-57 step 5): an approval is the approver's decision under STD-01, not a council decision on a `GV-###` issue.
- Approving POL-04 and POL-06 sets the rules; the environment doesn't meet them yet (GOV-70 to GOV-74, GOV-82). The approvers say so in their comments.
- Employee IDs follow roster order (row n → EMP1000(n-1)), consistent with the existing STD-01 acknowledgment rows.

### Open / next
- Owner decisions: the AI-tools position (GOV-76 → POL-05); who must acknowledge the policies (POL-01 says all staff, which includes drivers) before acknowledgment rows are added.
- Tickets to draft for owner approval: first tabletop (May 2027, POL-08); first risk register entry, the card-data risk (POL-06, GOV-86); first annual risk assessment (POL-06).
- Acknowledgment rows for the seven policies: not yet added (pending the audience decision). The closing comments say so.
- Process: before merging, check the PR's commit list matches the branch (`gh pr view N --json commits`).

---

## 2026-11-24 — Audit findings F1 to F7 recorded (GOV-82)

### Done
- **GOV-82** (Story, label `audit-finding`): "Audit findings: policy drafting, Nov 24, 2026". Sub-tasks, each labelled `audit-finding`, with the requirement broken, severity and the reason for it:
  - GOV-83 F1 (Medium): changes merged to `main` without a PR or second reviewer
  - GOV-84 F2 (High): SOC 2 matrix marks IR-01/IR-02 "Implemented" with no plan
  - GOV-85 F3 (High): evidence tracker PBC-002 "Collected" with no risk register
  - GOV-86 F4 (High): no risk register; card-data risk (score 15) neither accepted nor treated
  - GOV-87 F5 (Medium): console changes recorded only in the worklog
  - GOV-88 F6 (High): no incident response plan or playbooks; no communications lead
  - GOV-89 F7 (Low): no break-glass admin account
- **PR #5** was created with the blank template; Claude added the full description afterwards at the owner's request, with a note at the top. Claude's review records it as a POL-07 5.3 deviation (second after PR #3).

### Decisions
- **Severity scale** (owner agreed the ratings and asked for the reasons): **High** = a record states something untrue about a control or its evidence, or a required control is missing where card data or a High risk is exposed; **Medium** = control defined but not operating as written, partly offset by another record; **Low** = good practice missing, little effect on data or audit conclusions. Each ticket says why it isn't one level higher or lower.
- Findings stay unfixed (owner decision); each names its planned fix. F8 became council issue GV-007, not a finding.

---

## 2026-11-24 — Story GOV-81 for the follow-ups; council issue GV-007 added

### Done
- **GOV-81** (Story, no epic): "Policy drafting follow-ups", grouping GOV-75 to GOV-80. Converted from Tasks to sub-tasks of GOV-81 with Jira's Move (owner approved). Status stays To Do; the default Priority field was dropped; the blocking links were kept.
- **GV-007** added to the council charter backlog (section 11): who stewards cardholder data, Rider or Finance. It's backed by planted scenario **S11**: `raw.payments_rider_cards` rows list `rider-data-steward`; `staging`/`marts` card rows list `finance-data-steward`; the owner is `cfo` throughout. The first council issue under the `GV` prefix.

- **PR prep rule changed** (owner request): pre-filled links were too long. Claude now gives a short compare link and puts the full description on the clipboard; descriptions must list every file and change, the commits, the evidence, what wasn't changed, and full Jira/Confluence links (CLAUDE.md #3, memory).

### Decisions
- The card-data steward question is a planted defect (S11), not a new finding, so it goes to the council (GV-007), not to the audit-findings list. The S11 rows are left as found.

---

## 2026-11-24 — 6 follow-up tickets created (GOV-75 to GOV-80)

### Done
Owner approved all 6 drafts. Created as Tasks with no epic:
- **GOV-75** Security incident reporting channel. Blocks GOV-55 (POL-01) and GOV-62 (POL-08).
- **GOV-76** Approved tools list (software and AI, by data tier). Blocks GOV-59 (POL-05).
- **GOV-77** Protect `main` with a GitHub ruleset (owner UI change; it's the POL-07 5.9 change record).
- **GOV-78** Retire the repo `access-control-policy.md` (pointer to POL-02).
- **GOV-79** Line up ACC-02/ACC-03 with POL-02's 24-hour and 5-day deadlines.
- **GOV-80** Move the Classification and Labeling standards to Confluence as STD-02 and STD-03.

### Risks
- PR #3 was created with the blank template, not the prepped description, so it didn't meet POL-07 5.3 (description complete at creation). Claude recommended closing it unmerged and creating a new PR from the prepped link. This is the first time the review step caught a miss.

---

## 2026-11-24 — POL-07 small-team allowance rewritten for one maintainer; PR #2 reviewed

### Done
- **PR #2** (created by the owner, the first under the new rule) reviewed by Claude as a PR comment: ready to merge.
- **POL-07** (page v3, still document v0.9), owner change after review:
  - The section 6 small-team allowance now describes the real flow: PR drafted by the author or Claude; the maintainer creates it; Claude posts a written review before merge; the maintainer merges (the merge is the approval); every use counts in the quarterly sample. It's labeled a compensating control, not separation of duties, and still never covers IAM, security or cardholder-data changes.
  - 5.3 now requires the PR description at creation.
  - The gaps panel says PRs started with PR #1.
  - Noted in the 0.9 change-history row and in a GOV-10 comment for the approver.

### Decisions
- No simulated re-review: it's an owner change, flagged for the approver (GOV-61) instead, the same way DOC-01's in-cab addition was handled.

---

## 2026-11-24 — Pull-request workflow; council IDs renamed GOV → GV

### Done
- **Council IDs renamed** at the owner's request: issues `GOV-###` → `GV-###`, decisions `GOV-D-###` → `GV-D-###` (charter, classification register, CLAUDE.md, this log). The charter now says why: `GV` is the council register, `GOV` is the Jira project. No Confluence page or Jira ticket used the old IDs (searched).
- **Pull-request workflow** (owner decision): every change reaches `main` through a PR. **Refined the same day (owner chose option 2): Claude preps the PR and gives a pre-filled link; the owner clicks Create.** PR #1 was opened by Claude before this refinement. Each PR gets a full description at creation (new `.github/pull_request_template.md`, aligned with POL-07: change type, DOC-01 scope check, testing, rollback) and posts a review comment. CLAUDE.md agreement #3 and memory updated.

### Decisions
- **Claude can review but not approve in GitHub.** Claude acts through the owner's account (2Wake), and GitHub blocks authors from approving their own PRs. So the owner is the approver (by merging or explicitly telling Claude to merge). An AI review is evidence a review happened; it isn't segregation of duties between two people. That's the honest compensating control for a one-person repo.

### Next steps
- POL-07's small-team allowance should describe this workflow before approval (owner to confirm).
- Proposed tickets (incl. protecting `main` with a ruleset, owner UI change), then the audit findings.

---

## 2026-11-24 — Policies POL-01 to POL-08 drafted and reviewed to v0.9 (parallel)

### Done
- New Confluence folder **Policies** (458802) under Policy Management.
- **POL-01 Information Security Policy** (491531) written first as a v0.1 frame, so the 7 topic policies could cite it. Then 7 parallel agents each drafted one policy from the approved template, ran its simulated review (dated today, marked [Simulated], ≥1 accepted and ≥1 rejected-with-reason) and closed its draft + review sub-tasks with closing comments.
  | ID | Page | Story | Approval sub-task |
  |---|---|---|---|
  | POL-01 Information Security | 491531 | GOV-4 | GOV-55 (CEO) |
  | POL-02 Access Control | 557061 | GOV-5 | GOV-56 |
  | POL-03 Data Classification & Handling | 426094 | GOV-6 | GOV-57 |
  | POL-04 Cardholder Data Protection | 557113 | GOV-7 | GOV-58 (CFO + CISO) |
  | POL-05 Acceptable Use | 426073 | GOV-8 | GOV-59 (VP People + CISO) |
  | POL-06 Risk Management | 557136 | GOV-9 | GOV-60 |
  | POL-07 Change Management | 557087 | GOV-10 | GOV-61 |
  | POL-08 Incident Response | 458805 | GOV-11 | GOV-62 |
- POL-01 v0.2 folded in the agents' findings (card data → POL-04, risk acceptance roles, yearly acknowledgment, security reporting channel, change management, monitoring notice, CFO/GC roles, POL-04 exceptions need CFO+CISO, links). Leadership review (GOV-40) → v0.9: accepted classification-drives-controls and lawful monitoring with §52-c notice; rejected CDO co-ownership (one accountable owner, STD-01 s8). GOV-25, GOV-40 Done.
- Register page v6 + extract: POL-01 to POL-08 `in_review`, 0.9, page IDs.
- Approval sub-tasks (GOV-55 to GOV-62) untouched, waiting for the owner.

### Decisions
- Draft the umbrella first, approve it first or same day (owner agreed). Shared files (register, CSV, WORKLOG, git) kept with the main session so parallel agents can't collide.

### Found (audit material; not fixed)
- No security incident reporting channel exists (POL-01 s7, POL-08 s1 point to it). Blocks approval of POL-01 and POL-08.
- No approved tools list (software/AI by data tier) for POL-05. Blocks GOV-59.
- POL-07 walk-through: today's merges went straight to `main` (no PR, no second reviewer); `main` has no branch protection; console changes recorded only in WORKLOG.
- SOC 2 control matrix marks IR-01/IR-02 "Implemented" but no IR plan exists; evidence tracker PBC-002 says Q1–Q4 risk register exports "Collected" but no register exists.
- Council charter's issue IDs clashed with Jira GOV keys. **Resolved 2026-11-24 at the owner's request:** council IDs renamed to `GV-###` / `GV-D-###`.
- Card-data stewardship unclear (register says Rider steward, table owner label is CFO); referred to council in POL-03.
- `01-governance-program/governance/access-control-policy.md` superseded by POL-02; ACC-02/ACC-03 have no 24h / 5-day allowance matching POL-02 s6–7.
- Classification & Labeling standards still repo-only (DRAFT v0.1); proposed to move to Confluence as STD-02/STD-03.

### Next steps
- Owner decides on proposed tickets, then approvals in order: POL-01 (CEO) first.

---

## 2026-11-24 — GOV-2 closed: DOC-01 approved v1.0; observations story GOV-70

### Done
- **DOC-01 approved v1.0** *[Simulated]*: CFO consulted comment (Confluence 458789), CISO "Approved version 1.0" comment (491527) with next scope confirmation 2027-11-24 and scope-reduction ideas as follow-ups. Page v4: banner, version, status, approval date, next confirmation, 1.0 change-history row, section 5 links to GOV-70–74. Register page v5 + extract: `approved,1.0,2026-11-24,2027-11-24`.
- **GOV-70 (Story, not under an epic; owner decision)** "PCI scope observations: plan remediation by policy", linked Relates → GOV-2 and to DOC-01. Sub-tasks bucketed by governing policy:
  - GOV-71 encryption (obs. 1, POL-11/GOV-14)
  - GOV-72 access need-to-know (obs. 2, POL-02/GOV-5)
  - GOV-73 retention & disposal (obs. 3, 5, POL-13/GOV-16)
  - GOV-74 card-data location inventory (obs. 4, POL-04/GOV-7)
- Closing comments posted, then Done: **GOV-21**, **GOV-2** (GOV-2's comment lists all 5 observations with their sub-task, plus the 3.5 unknowns).

### Decisions
- Section 3.5 unknowns (processor, app TLS, in-cab provider) are questions, not remediation: they stay with GOV-15, not GOV-70.
- Observations stay unremediated until their governing policy is approved (audit material).

### Risks
- GOV-73: `raw` is append-only by design, which conflicts with deleting expired card data. Needs a design decision when POL-13 is written.

---

## 2026-11-24 — DOC-01 in-cab payments added; atlassian-setup merged to main

### Done
- **DOC-01** (page v3, still document v0.9): owner asked to add in-cab card payments. Added to 3.5 *Not yet known* (provider, path, whether card data returns to ECT; Finance to confirm, vendor inventory GOV-15), as a second entry point on the data-flow diagram, and as a transfer-table row. Recorded in the 0.9 change-history row as an owner addition after review.
- **Merged `atlassian-setup` → `main`** (owner chose "Claude merges directly"). Fast-forward, no conflicts; main at 3831ec1. The Arjun roster correction (2026-11-24) is now on main before the next daily run (10:30 UTC Nov 25), which is the first run to generate Nov 24.

### Next steps
- Owner approves the drafted story + 4 sub-tasks for the DOC-01 observations (bucketed by policy: encryption, access, retention/disposal, cardholder data inventory).
- GOV-2 closing comment will list observations 1–5 and point to the new story; posted when GOV-21 sign-off is recorded.

---

## 2026-11-24 — How-To's folder: reading DOC-01 and running a PCI scoping exercise

### Done
- New Confluence folder **How-To's** (458756) under the ECTG home.
- **How to read DOC-01 PCI DSS Scope & Cardholder Data Flow** (458759): PCI DSS basics (PAN, CHD vs sensitive authentication data, 12 requirements, QSA vs SAQ) and a plain-language walkthrough of every DOC-01 section, mapping each observation to its PCI requirement and the policy that will handle it.
- **How to run a PCI DSS scoping exercise** (426044): 7-step method (set up → payment channels from Finance → follow the data with 5 questions → discovery scans → classify with decision table → draw and cross-check the flow → review, sign off, re-scope triggers), who does what, and a system-owner questionnaire.

### Risks / gaps found
- Applying the method's "payment channels" step to ECT shows **in-cab card payments are missing from DOC-01** (NYC taxis take cards in the cab, usually through a third-party terminal provider). Flagged to the owner; DOC-01 not yet changed.

---

## 2026-11-24 — GOV-2: DOC-01 PCI DSS scope drafted and reviewed (v0.9)

### Done
- **DOC-01 PCI DSS Scope & Cardholder Data Flow** created in ECTG (page 425996, under the space home). Linked from GOV-2.
  - **Inventory (GOV-19 → Done)** from read-only checks: BigQuery column scan and `pci_scope` labels across raw/staging/marts; current access records; access policy matrix; role service accounts; workflow; local `output/`.
    - In scope: S1 rider app card entry, S2 payments system (simulated by the generator), S3 Actions runner, S4 `raw.payments_rider_cards`, S5 `staging.stg_payments_rider_cards`, **S6 `staging.stg_payments_rider_cards_history`** (not in the ticket's starting list), **S7 laptop `data-platform/output/`** (327 days of full PAN in plain JSONL, 213 MB total, gitignored), S8 Google Cloud, S9 GitHub. Access: A1 `ect-pipeline`, A2 `ect-role-security`, A3 `ect-role-steward`, A4 36 people with raw/staging grants (dataset-level, includes 4 `data_analyst` grants on raw), A5 project owners.
    - Connected-to: C1 repo/workflow, C2 Workload Identity provider, C3 `marts.dim_rider_cards` (the last-4 step), C4 Cloud audit logging (added in review).
    - Out of scope: other marts, DQ/defect tables (IDs only), `ect-role-analyst`, Looker Studio, Atlassian, Collate (not connected; re-assess before connecting).
  - **Data flow (GOV-20 → Done):** text diagram with CDE boundary + transfer/protection table.
  - Observations recorded, not remediated: clear PAN in raw + 2 views; 36 readers via dataset-level access; laptop PAN files with no retention; S6 previously untracked; 3y retention label pending POL-13.
- **Simulated review, in the right order this time** (dated today): Mateo Silva (accepted: add C4), Owen Park (rejected with reason: move laptop to connected-to; agreed). Page → **v0.9, In review**. Register page + extract: DOC-01 `in_review`, 0.9, page 425996.
- GOV-2 → In Progress; GOV-21 (CISO sign-off) → In Review, **waiting for the owner's go-ahead**.

### Decisions
- Staging view name is `stg_payments_rider_cards` (earlier notes said `stg_rider_cards`).
- Scope follows the data: synthetic but real-format PANs are treated as real, so the laptop is in scope.

### Next steps
- Owner reviews DOC-01 → record CISO approval v1.0 (CFO consulted), next scope confirmation 2027-11-24, scope-reduction ideas as follow-ups (GOV-21). Then GOV-2 closes and GOV-7/14/15 unblock.

---

## 2026-11-24 — Roster fix: Arjun Mehta role_code (generator 0.3.0)

### Done
- **User asked to fix** the missing `role_code` for Arjun Mehta (VP Engineering, EMP10064). The register names `vp-engineering` as owner of POL-07.
- `org_roster.csv`: role_code `vp-engineering` added.
- **Applied as a dated HR correction, not a rewrite of history.** New `ROSTER_CORRECTIONS` in `config.py` (`arjun.mehta: 2026-11-24`). Before that day the record keeps a blank role_code exactly as loaded. On Nov 24 (the first day not yet loaded; raw is loaded through Nov 23) the simulation emits a new version of his HR record with the role code. It uses its own random stream, so nothing else changes.
- `GENERATOR_VERSION` 0.2.0 → **0.3.0** (output from Nov 24 on differs: his new record version, and he now counts as a role holder).
- **Verified:** batches for Jan 1, Jun 15, Nov 22 and Nov 23 hash-identical between the old code (0.2.0, checked out separately) and the new code. New test `test_roster_correction_arrives_on_its_day_and_leaves_history_unchanged`; pytest 13/13.

### Decisions
- Fix forward with a dated correction so `raw` stays append-only and `stg_hris_employees_history` shows the blank → `vp-engineering` change on Nov 24 (an honest record that HR data was corrected).

### Next steps
- Takes effect in BigQuery after `atlassian-setup` is merged to `main` and the daily run generates Nov 24. **If tonight's daily run (from `main`) generates Nov 24 before the merge, the correction must move to the next unloaded day.**

---

## 2026-11-24 — Single source of truth; STD-01 v2.0 after late review; acknowledgments seed

### Done
- **Option (b) for the STD-01 review gap: an honest late review, dated today.** On the STD-01 page:
  - *[Simulated]* comments from Elena Popescu (GRC Analyst) and Robert Feld (General Counsel), and author replies from Jordan Ellis.
  - Elena: remove repo copies (one source of truth) → **accepted**.
  - Robert: Legal sign-off on every exception → **rejected with reason** (section 10 already bars waiving legal/regulatory/PCI requirements); compromise accepted by Robert: owner must consult General Counsel on exceptions touching legal, regulatory or contractual obligations.
  - Changes a responsibility → **major change, v2.0** (STD-01 section 6). Sections 4, 10, 11 revised; change-history row explains the late review. *[Simulated]* "Approved version 2.0" comment from Victor Hale, CISO. Next review unchanged (2027-11-24).
  - The v1.0 approval comment relabeled *[Simulated]*.
- **Policy Register:** STD-01 → v2.0; intro now says the page is the only source of truth and the repo seed is an extract; change-log entry. `policy_register.csv` updated.
- **Space home page:** warning panel disclosing that ECT is fictional and staff reviews/approvals/acknowledgments are simulated, posted from the owner's account, never backdated.
- **Repo copies deleted:** `01-governance-program/policies/` removed (created earlier today).
- **New seed `policy_acknowledgments.csv` (simulated)**: one row per employee per approved document version (`ack_id`, `doc_id`, `doc_version`, `employee_id`, `basis`, `assigned_on`, `due_on`, `acknowledged_on`, `evidence`). STD-01 v2.0: 19 people (policy owners/approvers, policy admins, data stewards who author, named reviewers), due 2026-12-08 (10 business days). 4 acknowledged today through their review/approval comments (evidence = Confluence comment IDs); 15 pending. Tests: `ack_id` unique/not null, `doc_id` must exist in `policy_register`. All 19 employees confirmed active in `stg_hris_employees` (read-only, capped query). `dbt parse` OK, pytest 12/12.
- **Jira:** decision comment on epic GOV-1 withdrawing every "copy to the repo" step in its 29 open tickets (descriptions left as written, as history).

### Decisions
- **Confluence is the single source of truth for policy text (user).** No policy copies in the repo, no blog/announcement post: Confluence page history and Jira record what was published and when. Recorded in `CLAUDE.md` #5 and STD-01 v2.0.
- **Simulation rules (user agreed):** simulated staff responses are labeled *[Simulated]*, dated the day they're recorded, and never backdated to hide a gap.
- The `policy_register` seed stays as an *extract* (dbt can't read Confluence). A later automation (Project 3) could generate it from the page.
- Acknowledgments use employee IDs, not names (data rule).

### Risks / audit material (not fixed)
- STD-01 v1.0 was approved before review (late review recorded in v2.0).
- `01-governance-program/governance/access-control-policy.md` (Project 1) is a second access control policy outside Confluence; resolve when POL-02 is drafted.
- Org roster: Arjun Mehta (VP Engineering) has no `role_code`, but the register names `vp-engineering` as POL-07 owner.
- New seed columns not in the classification register (CLS-01).

### Next steps
- GOV-2: PCI DSS scope (DOC-01).
- Dec 1: record further STD-01 acknowledgments; leave some missing past the Dec 8 due date as a gap.

---

## 2026-11-24 — STD-01 and template approved; GOV-3 closed; closing-comment rule

### Done
- **User approved STD-01 Policy Management Standard and the Policy Template.** Recorded per STD-01 section 8 (three places):
  1. STD-01 page: status banner APPROVED v1.0, version 1.0, approval/effective date 2026-11-24, next review 2027-11-24, v1.0 change-history row (approver Victor Hale, CISO).
  2. "Approved version 1.0" footer comment on the STD-01 page.
  3. Policy Register page: STD-01 row Approved, v1.0, dates filled; change-log entry. `policy_register.csv` updated to match.
  - Policy Template page: green "Template status: APPROVED v1.0" banner added. The DRAFT placeholders stay, because they're for the new policy copied from it.
- **Repo copies of approved documents:** new folder `01-governance-program/policies/` with `README.md` (index), `STD-01-policy-management-standard.md`, `policy-template.md`. (The Confluence markdown export dropped dates; restored by hand.)
- **Jira:** GOV-24 and GOV-3 → Done. Closing comments added to GOV-22, GOV-23, GOV-24 and GOV-3.

### Decisions
- **New working rule (user):** every ticket gets a closing comment before Done: *What happened* + *Open items*. Added to `CLAUDE.md` agreement #5.
- The Policy Template is not a numbered register document; its approval is recorded on its page and in the register change log.

### Risks / audit material (not fixed)
- STD-01 went from v0.1 straight to v1.0: no recorded comments from the named reviewers (Elena Popescu, Robert Feld) and no v0.9, which STD-01 section 7 requires. Approval comment was posted from the site owner's account on the CISO's behalf.
- The staff announcement of STD-01 within 10 business days (section 11) is not yet sent.

### Next steps
- GOV-2: PCI DSS scope & cardholder data flow (DOC-01). Then tomorrow's 8 policies.

---

## 2026-11-24 — GOV-22 approved; GOV-23 Policy Register built

### Done
- **GOV-22 Done:** user approved STD-01 Policy Management Standard and the Policy Template ("look great").
- **GOV-23 Done: Policy Register built in two places.**
  - **Confluence:** *Policy Register* page (65685) in the Policy Management folder. One row per document (17: STD-01, DOC-01, POL-01 to POL-15) with type, owner, approver, status, version, approval date, next review, Jira key and page link. All start as Draft. Includes a change log.
  - **Repo:** `data-platform/dbt/seeds/governance/policy_register.csv` plus its entry in `seeds/_seeds.yml` (description, labels, tests: `doc_id` unique/not null, `doc_type` and `status` accepted values). `dbt parse` passes and the 5 new tests are registered; `pytest` 12/12 pass.
  - `dbt/README.md`: added `seeds/governance/` to the layout table and a note on keeping the CSV in sync with Confluence (Confluence wins; same-session update by pull request).
- **Space home page updated:** replaced the template's placeholder description with a real one, and added a *Key documents* section linking the register, STD-01 and the template.

### Decisions
- Seed columns: `doc_id, title, doc_type, owner_role, approver_roles, status, version, approval_date, next_review_date, jira_key, confluence_page_id`. Roles are org-roster role slugs (labels rule: no names in data); `approver_roles` is `;`-separated for joint approvals (POL-04 CFO+CISO, POL-05 VP People+CISO).
- **The seed is not loaded to BigQuery yet.** It loads on the first daily `dbt build` after this branch is merged to `main`; it wasn't run locally to avoid writing to the shared `staging` dataset from a feature branch.
- **Planted register gaps (overdue review, unapproved policy, etc.) are not in yet.** They go in when approvals are recorded, so the register first reflects real progress.

### Risks
- The new seed's 11 columns land in `staging` without classification register entries, so CLS-01 (unclassified columns) will count them, like the other governance seeds. Consistent with the existing open CLS-01 finding; not fixed, per the findings rule.

### Next steps
- GOV-24: STD-01 review and CISO approval (record approval in all three places).
- GOV-2: PCI DSS scope & cardholder data flow (DOC-01).

---

## 2026-11-24 — GOV-22 drafted; schedule compressed; dependencies linked

### Done
- **GOV-22 (policy management standard + template): drafted in Confluence.** New folder **Policy Management** in `ECTG`, with:
  - **STD-01 Policy Management Standard** (draft v0.1, page 327917). Covers document types, roles, numbering, versioning, lifecycle, who approves what, the 12-month review cycle, exceptions and where documents are published.
  - **Policy Template** (page 65668): document control table, 8 standard sections and a change history.
  - Both pages linked on GOV-22. GOV-22 → **In Review**; GOV-1 and GOV-3 → **In Progress**.
- **Schedule compressed (user: "everything will wrap quickly").** Working days are Tue Nov 24, Wed Nov 25 and Tue Dec 1 (off Thu/Fri for the holiday). All 69 tickets re-dated, verified by JQL:
  - **Nov 24:** GOV-3 (register & standard), GOV-2 (PCI scope).
  - **Nov 25:** GOV-4 Info Security, GOV-5 Access Control, GOV-6 Classification, GOV-7 Cardholder Data, GOV-8 Acceptable Use, GOV-9 Risk, GOV-10 Change, GOV-11 Incident Response.
  - **Dec 1:** GOV-12 Logging, GOV-13 Vulnerability, GOV-14 Encryption, GOV-15 Vendor, GOV-16 Retention, GOV-17 HR Security, GOV-18 BC/DR.
  - Epic GOV-1: Nov 24 – Dec 1.
- **22 "Blocks" links added** (show as dependency lines on the Timeline):
  - GOV-3 blocks every policy story (GOV-4 … GOV-18).
  - GOV-2 (PCI scope) blocks GOV-7, GOV-14, GOV-15.
  - GOV-7 (Cardholder Data) blocks GOV-14 (Encryption).
  - GOV-5 (Access Control) and GOV-8 (Acceptable Use) block GOV-17 (HR Security).
  - GOV-9 (Risk) blocks GOV-13 (Vulnerability; exceptions use risk ratings).

### Decisions
- **Document numbering set in STD-01:** POL-xx policies, STD-xx standards, PRC-xx procedures, DOC-xx supporting documents. Planned IDs: POL-01 Information Security, POL-02 Access Control, POL-03 Data Classification & Handling, POL-04 Cardholder Data Protection, POL-05 Acceptable Use, POL-06 Risk Management, POL-07 Change Management, POL-08 Incident Response, POL-09 Logging & Monitoring, POL-10 Vulnerability & Patch, POL-11 Encryption & Key Management, POL-12 Vendor & Third-Party Risk, POL-13 Data Retention & Disposal, POL-14 HR Security, POL-15 BC/DR; DOC-01 PCI DSS Scope & Cardholder Data Flow.
- **Approval evidence in three places** (document control table, approver comment on the page, register) so an auditor can cross-check.
- Exceptions are raised in Jira GOV, max 12 months, and can't waive PCI DSS requirements.
- Classic Confluence **pages** (not live docs) for policies, for version history and approvals.

### Risks
- A Jira automation moved GOV-23/24 to In Progress when GOV-3 moved; reset to To Do.

### Next steps
- User reviews STD-01 and the template. Then GOV-23 (Policy Register page + `policy_register` seed), GOV-24 (approval), and GOV-2 (PCI scope), all today.

---

## 2026-11-24 — Jira timeline: start and due dates on all 69 tickets

### Done
- Moved the uncommitted CLAUDE.md / WORKLOG changes off `main` to branch **`atlassian-setup`** and pushed it (user asked). Not merged.
- **Set Start date and Due date on every GOV ticket (69/69, verified by JQL)** so the Jira Timeline tab shows the plan. Field: `Start date` = `customfield_10015`; due = `duedate`.

  | Wave | Stories | Dates |
  |---|---|---|
  | Foundation | GOV-3 Register & standard | Nov 30 – Dec 11 |
  | Foundation | GOV-2 PCI scope | Dec 7 – Dec 23 |
  | Wave 1 | GOV-4 Info Sec, GOV-5 Access, GOV-6 Classification, GOV-9 Risk | Dec 14 – Jan 22 |
  | Wave 2 (needs PCI scope) | GOV-7 Cardholder Data | Jan 4 – Feb 5 |
  | | GOV-14 Encryption, GOV-15 Vendor | Jan 11 – Feb 12 |
  | Wave 3 | GOV-8 Acceptable Use, GOV-17 HR Security | Jan 18 – Feb 19 |
  | | GOV-10 Change, GOV-11 Incident Response | Jan 25 – Feb 26 |
  | Wave 4 | GOV-12 Logging, GOV-13 Vulnerability | Feb 1 – Mar 5 |
  | | GOV-16 Retention, GOV-18 BC/DR | Feb 15 – Mar 19 |
  | Epic | GOV-1 | Nov 30, 2026 – Mar 19, 2027 |

### Decisions
- **Standard rhythm per policy:** draft 2 weeks → review 2 weeks → approval & publish 1 week. Wave 1 drafts are shortened to Dec 14–23, then review resumes Jan 4 (no work scheduled Dec 24 – Jan 1).
- **Dependencies built into the dates:** policy template approved (Dec 11) before any policy draft starts; PCI scope approved (Dec 23) before card-data policies start; Cardholder Data approved (Feb 5) before Encryption approval (Feb 8–12); Access Control approved (Jan 22) before HR Security review (Feb 1).
- At most 4 policies in review at once, to spread approver load.

### Risks
- Dependencies are only in the dates, not Jira links; a slip won't move dependent tickets automatically.
- Approver availability (CISO approves 9 policies) is the biggest schedule risk.

### Next steps
- Start GOV-22 (policy template & standard) on Nov 30.

---

## 2026-11-24 — Jira: policy-set epic created (GOV-1 to GOV-69)

### Done
- **Created 69 tickets in Jira project `GOV`** (user approved the format and said "create the tickets"):
  - **GOV-1 (Epic):** Information Security Policy Set (SOC 2 · ISO 27001 · PCI DSS).
  - **GOV-2 to GOV-18 (Stories, 17):** GOV-2 PCI DSS scope & cardholder data flow; GOV-3 Policy Register & policy management standard; then one per policy: GOV-4 Information Security (umbrella), GOV-5 Access Control, GOV-6 Data Classification & Handling, GOV-7 Cardholder Data Protection, GOV-8 Acceptable Use, GOV-9 Risk Management, GOV-10 Change Management, GOV-11 Incident Response, GOV-12 Logging & Monitoring, GOV-13 Vulnerability & Patch, GOV-14 Encryption & Key Management, GOV-15 Vendor & Third-Party Risk, GOV-16 Data Retention & Disposal, GOV-17 HR Security, GOV-18 BC/DR.
  - **GOV-19 to GOV-69 (Subtasks, 51):** 3 per story. GOV-2: inventory → data-flow diagram → CISO scope sign-off. GOV-3: standard & template → register page + `policy_register` seed → CISO approval. Policy stories: **draft** (GOV-25–39) → **review** (GOV-40–54) → **owner approval & publish** (GOV-55–69).
- Every ticket has Description (with steps), Why it matters, Potential blockers, Intended outcome. Owners, approvers and reviewers are named people from the org roster. Labels: `policy-set` on all, `pci` where card data is involved.

### Decisions
- **Combined policy set** for SOC 2, ISO 27001 and PCI DSS (user confirmed).
- **No framework mapping in the policy tickets** (user): mapping comes later in a separate **Common Control Framework (CCF)** project.
- **Jira hierarchy convention (user):** Epic = large project; Story = medium piece within it; Subtask = daily/weekly task.
- Planted policy gaps are **not** visible in tickets; the answer key stays in the repo.

### Next steps
- Start GOV-3 (policy management standard + register), then GOV-2 (PCI scope), then the policies.
- Later epic: Common Control Framework.

---

## 2026-11-24 — PCI DSS added to the policy scope; Jira structure

### Done
- The user asked whether payment data means PCI DSS applies, not just SOC 2. **Yes.** The README already says ECT must meet PCI DSS. Also, `raw.payments_rider_cards` and `staging.stg_rider_cards` hold **full card numbers, expiry dates and cardholder names**, so BigQuery `raw` and `staging` (and the pipeline that writes them) are in the cardholder data environment (CDE). Only `marts.dim_rider_cards` (last 4 digits) is out of scope.
- The control matrix (`02-soc2-iso-audit/control-matrix.csv`) maps to SOC 2, ISO 27001 and NIST only. **It has no PCI DSS column.**

### Decisions (proposed, awaiting the user)
- **One policy set mapped to SOC 2 + ISO 27001 + PCI DSS v4.0.1**, not a separate PCI set. PCI Req 12.1 needs an information security policy anyway, and each PCI requirement asks for documented policies. Add PCI-specific content: CDE scoping and card-data flow, a Cardholder Data Protection policy, targeted risk analyses (12.3.1), service-provider management (12.8).
- **Jira structure (user's rule):** Epic = large project; Story = medium piece within it (e.g. one policy); Subtask = daily/weekly task (drafting, mapping, review, approval).

### Risks / findings (left open for the audit)
- **Full card numbers stored in clear in the warehouse.** BigQuery's default encryption is storage-level, which PCI DSS 4.0.1 (3.5.1 / 3.5.1.2) doesn't accept on its own for non-removable storage. Storing card numbers in an analytics warehouse also conflicts with data minimization (3.2.1). Not planted, but realistic. Not fixed, per the findings rule.

---

## 2026-11-24 — Atlassian connected; split confirmed

### Done
- **Atlassian MCP connected** (official Rovo MCP, user sign-in). Site `empire-city-taxi.atlassian.net`.
- **User set up the workspace in the UI:** renamed the Jira project key from the default `KAN` to `GOV` (project "ECT GRC", no issues yet). Created the Confluence space **Empire City Taxi Governance** (`ECTG`). Claude verified both with read-only checks.
- **The default "My first space" (`MFS`) is still on the site.** It's unused; the user can delete or archive it in the UI if they want.

### Decisions
- **Split confirmed by the user:** Confluence holds policy text, minutes and process docs. Jira holds planning, findings, remediation and audit requests. The repo holds what the pipeline reads plus a copy of each published policy, because the Atlassian site is private and the repo is the public portfolio. WORKLOG stays the decision log. Recorded in `CLAUDE.md` working agreement #5.

### Next steps
- SOC 2 policy set (~14 policies) in Confluence, with planted gaps, plus the policy register seed in the repo.

---

## 2026-11-24 — Plan: Jira + Confluence, then SOC 2 policies and a controls framework

### Decisions (direction agreed with the user; details to confirm)
- **Policies before more data work.** Project 2's control GOV-01 claims an information security policy set that doesn't exist; an auditor's first request would expose it. Plan: ~12–14 policies scoped to Security, Availability and Confidentiality, plus a **policy register** seed (owner role, approver, version, approval date, next review). Plant gaps for the audit: an overdue review, an unapproved policy, a control with no policy, a policy with no control, and a policy the data contradicts (e.g. leaver revocation within 24h vs. ACC-02). Full set vs. core 8: not yet decided.
- **Then a controls framework as data:** move `02-soc2-iso-audit/control-matrix.csv` into dbt seeds linking policy → control → SOC 2 / ISO 27001 / NIST → owner (roster role; "GRC Lead" and "IT Manager" don't exist in the roster) → automated check (ACC / CLS / DQ) → evidence. This is the start of Project 3 (continuous control monitoring).
- **Atlassian for planning and documents:** the user is creating a free Atlassian Cloud site (Jira + Confluence). Site addresses can't be renamed on the free plan, so pick a company-style name once. Connection through Atlassian's official remote MCP server (Rovo MCP; one server for both products; browser sign-in; nothing installed locally).
- **Proposed split (to confirm):** Confluence holds policy text, minutes and process docs. Jira holds planning, findings, remediation and audit requests. The repo keeps everything the pipeline reads (policy register, control framework, issue register) and a copy of each published policy, because the Atlassian site is private and the repo is the public portfolio. WORKLOG stays the decision log.

### Risks
- Two places for documents can drift; the policy register in the repo records each Confluence page's link and version to keep them tied.

- **Confirmed by the user:** Claude creates Confluence pages directly (with a summary in chat); Jira tickets are drafted for approval and always have Description / Why it matters / Potential blockers / Intended outcome. **Full policy set** (not core 8), written once the MCP is connected. Recorded in `CLAUDE.md` working agreement #5.

### Next steps
- User: create the site, add the MCP (`claude mcp add --transport http --scope user atlassian https://mcp.atlassian.com/v2/mcp`, then `/mcp`).
- Confirm whether Claude may create pages and tickets directly or drafts them for approval.
- Start the policy set.

---

## 2026-11-24 — Real role accounts and the daily access check

### Done
- **User created three role service accounts in the console** (no keys): `ect-role-analyst`, `ect-role-steward`, `ect-role-security`. Each has BigQuery Job User on the project and Data Viewer on its datasets. `ect-pipeline` holds Service Account Token Creator on each of the three (granted per account, not project-wide). Verified with read-only checks.
- **Explained "borrowing" (impersonation)** at the user's request: the pipeline acting as a role account gets only that account's read-only access, so it can't widen its own. It's needed because a keyless service account can't sign in by itself, and only a real query proves enforcement.
- **Misconfigurations kept as audit findings** (user's decision): `ect-role-steward` on `raw` (deliberate), and `ect-role-analyst` on `raw` instead of `ect-role-security` (a setup slip the user chose to keep). Recorded in `seeds/governance/role_account_answer_key.csv`.
- **Built `uv run ect-access-check`** and added it to the daily workflow after `ect-daily`. For each account × dataset it records **config** (on the permission list?) and **enforcement** (acting as the account, does a dry-run query get accepted?). Results go to the new observed table `raw.iam_role_access_tests`, then `marts.fct_role_access_tests` (ACC-08 excess, ACC-09 missing, ACC-10 check failed) and `marts.fct_role_access_scorecard`. The run record gets an access table.
- Policy doc updated: `access-control-policy.md` → *Enforcement (real)*.

### Decisions
- **Design vs. operating effectiveness:** both checks are kept because they can disagree, and that disagreement is itself audit evidence.
- **Expected access comes from the policy matrix**, not from a separate list, so changing the policy changes the test.
- **Enforcement probes use what a user needs:** `raw.hris_employees`, `staging.stg_hris_employees` (a view), `marts.dim_employees`.
- The check never fails the daily run; problems are recorded as `error` (ACC-10).

### Risks
- **Expected first-run surprise:** staging models are *views* over `raw`. In BigQuery, querying a view also needs access to its source tables, unless the view's dataset is authorized on `raw`. So `staging` access probably only works for accounts that also have `raw`. If confirmed, that's a real design gap (the policy gives stewards staging without raw), fixable with an authorized dataset. Leave it as a finding.
- The enforcement path can't be tested locally (impersonation from the laptop is blocked), so the first GitHub Actions run is the real test.

### First run (2026-11-24, run 45437194376, started by Claude at the user's request): green
- 18 checks loaded into `raw.iam_role_access_tests`. dbt: 66 pass, 39 warn, 0 errors.
- **Scorecard: all 3 planted misconfigurations caught by both checks** (analyst on `raw`, steward on `raw`, security missing `raw`).
- **One unplanted finding, as predicted:** `ect-role-security` is *on* the `staging` permission list (config passes), but BigQuery refuses its query (enforcement fails, ACC-09). The refusal names `raw.hris_employees`, the table under the `staging` view. **Design gap:** staging views need `raw` access unless `staging` is authorized on `raw`, so the policy's "staging without raw" (stewards) can't work as built. Left open as an audit finding; the fix would be an authorized dataset.
- The steward's `staging` check passes only because of its (planted) `raw` access, so fixing that misconfiguration alone would expose the same gap for stewards.
- Small fix: refusal messages now keep only BigQuery's reason, not the request URL.

### Next steps
- Open findings for the audit: ACC-08/09 role accounts, the staging-view design gap, CLS-01 unclassified columns.

---

## 2026-11-24 — Org build-out and access control (simulated)

### Done
- **Merged to `main` directly** at the user's request (`612fad6`), and **`raw` rebuilt** with the user's approval: deleted the 10 generated tables (TLC sample and zones kept), regenerated 2026-01-01 → 2026-11-23 with v0.2.0 and bulk-loaded them. New `raw.iam_access_grants`: 214 rows (grant versions).
- **Full dbt build:** 143 nodes, 106 pass, 37 warn, 0 errors.
- **Access scorecard:** ACC-01 to ACC-07 caught **34 of 34** planted problems (100%), **0 false alarms**.
- **CLS-01 now flags 79 unclassified columns** (the new IAM table across raw/staging/marts and the new HR columns), as expected until the steward proposes classifications.
- **Decision (user, 2026-11-24):** the 79 unclassified columns are **left unclassified on purpose** as a finding for a future audit ("we need to have things to fix"). Don't remediate them.
- Active corporate staff per department now range from 8 (Legal & Privacy) to 28 (Customer Support).
- **Decision logged (user, 2026-11-24):** for classification changes, *"stewards propose and owners approve. Draft the changes as a steward would and I approve them."* Claude drafts as the steward; the user approves as owner.
- **Named roster** `data-platform/src/ect_platform/data/org_roster.csv`: 68 named people across 12 departments plus the CEO (the leaders and stewards from `governance-org-structure.md` plus 3–5 staff per department), each with a title, manager, role slug and access role. They are the first employees generated, so the CEO is `EMP10001` and Jordan Ellis is `EMP10003`.
- **HR data:** departments now match the org doc (12 departments). New columns `manager_id` and `role_code`. New lifecycle event: **transfers** between departments (movers).
- **Access policy matrix** `dbt/seeds/governance/access_policy.csv` (role × dataset → privilege, max classification, time limit, approver) and the policy doc `01-governance-program/governance/access-control-policy.md`. Analysts get `marts` only; security gets `raw` for 14 days per investigation; privacy gets rider `raw` for data subject requests.
- **New raw table `iam_access_grants`** (domain `risk`): grants on joining, revoked on leaving or transfer, expiring time-bound grants. 
- **Planted access scenarios ACC-01 to ACC-07** (analyst with raw, leaver not revoked, mover creep, self-approval, expired still active, no approval, wrong approver). Simulated through 2026-11-23: 183 grants, 27 planted defects across all 7 rules.
- **dbt:** `stg_iam_access_grants` (+ `_history`), ACC rules in `fct_dq_findings` and `dq_rules.csv`, `marts.fct_access_grants` (access review list) and `marts.dim_access_policy`; `dim_employees` gains `manager_id` and `role_code`.
- Generator version **0.2.0**. Tests: 12 pass (3 new: stable roster IDs and managers, unplanted grants follow the policy, business users and drivers have no access).

### Decisions
- **Roster inside the generator, not a separate seed:** named people must exist in HR data so grants, approvers and managers join to real employee IDs.
- **Named people never leave or transfer**, and employees carrying a planted access defect are protected from later random events, so a defect can't be cleaned up by accident.
- **`raw` needs a one-time rebuild**: departments and IDs change for all history, so v0.1 and v0.2 rows can't be mixed. All raw data is regenerable from the deterministic generator. Waiting for the user's go-ahead.

### Risks
- The scheduled run (05:30 New York) on `main` must not run between the merge and the rebuild, or it will fail on the new columns. Do both together.
- New columns are not yet in the classification register, so CLS-01 will flag them until the steward proposes classifications.

### Next steps
- Real role service accounts (3–4), set up by the user in the console, plus a verification test.

---

## 2026-11-24 — Column classification register (single source of truth)

### Done
- First fully green scheduled-style run confirmed earlier today; this work follows the user's question: *where is column classification held?*
- **Found:** column-level classification lived only in the stale Project 1 CSV (old table names, 27 of 96 raw columns missing, not loaded or used). Table labels were set in three places, and the marts cap test used a hard-coded column list.
- **Built** (approach approved by the user, who also asked for more wrongly-mapped scenarios):
  - **Register** `seeds/governance/column_classification_register.csv`: 500 rows covering every column in `raw`, `staging` and `marts`, with classification, category, treatment, owner, steward, status, proposed/approved by, and date.
  - **Answer key** `seeds/governance/column_classification_answer_key.csv`: 508 rows (18 Secret, 33 Confidential, 58 Sensitive, 361 Internal, 38 Public). Built from the Project 1 map, decisions for the new columns, and lineage (staging inherits from raw; marts follow masking, generalization and aggregation). It agrees with every table label and the marts cap.
  - **Checks** `marts.fct_classification_findings`: CLS-01 to CLS-08 (coverage, orphans, approval, table-label consistency, lineage drift, marts cap, steward mismatch, invalid tier), each a dbt warning test.
  - **Scorecard** `marts.fct_classification_scorecard`: register vs. answer key per column, plus which check flagged it.
  - **Process doc** `01-governance-program/governance/classification-register.md`.
- **12 planted scenarios (S01–S12), 36 register rows:** location (GV-003), free-text PII, partial cardholder data, regulated ID, consistent HR under-classification, lineage drift, over-classification, masked value, unclassified new columns, approval backlog, wrong steward, retired tier name.
- **First scorecard:** 27 of 508 columns wrong or missing; **24 flagged by checks**; the 3 unflagged are S05, a deliberate blind spot. **KPI #2 (high-risk columns correct): 72.5%** (37 of 51).
- Full dbt build: 126 nodes, 96 pass, 30 warn, 0 errors.

### Decisions
- **The register is the single source of truth**, kept in the repo and changed by pull request: steward proposes, owner approves, CISO or Privacy review Secret and Confidential changes. That is the federated model, and PR history is the audit trail. Collate and BigQuery tags will be fed from it later.
- **Operational register vs. answer key:** the register can be wrong, like real life; the answer key is used only to score it.
- **Register rows are per layer**, because classification can legitimately change between layers (masked, generalized, aggregated in marts).
- **CLS-05 flags both sides** of a raw/staging disagreement, since either could be the mistake.
- **The marts cap test stays on its fixed column list** as an independent safety net, because the register itself may contain mistakes.
- The Project 1 `column-classification-map.csv` is superseded but kept as a Project 1 artifact.
- The one-off bootstrap script was not committed; the CSVs are now maintained by hand through PRs.

### Next steps
- Remediation through the council (GV-003 first), council roles (federated), and DQ rule ownership columns.

---

## 2026-11-24 — Daily run (GitHub Actions); DQ rule ownership; federated model

### Done
- Merged `marts` to `main` from the CLI at the user's request (`8accce2`).
- **`uv run ect-daily`:** finds the newest loaded day (`MAX(_batch_date)` of `raw.app_trips`, ~3 MB read), then generates and loads every missing day through yesterday. A failed or skipped run is caught up the next day. Tested with a dry run: last loaded 2026-11-23, 0 days due.
- **`uv run ect-record`:** writes `data-platform/run-records/<date>.md` with the days loaded, row counts per table, and the dbt results (every warning or failure with its failing-record count). Counts and test names only, never data values.
- **Workflow** `.github/workflows/daily-refresh.yml`:
  - Runs daily at 10:30 UTC (5:30 am New York), plus a manual "Run workflow" button.
  - Steps: keyless Google sign-in → install → generator tests → `ect-daily` → `dbt build` → run record → commit.
- **Setup guide** `data-platform/docs/github-actions-setup.md`: console steps A–G for the user (APIs, service account, dataset access, Workload Identity pool and provider, impersonation grant, GitHub variables, test run).
- Read-only check: the IAM, IAM Credentials and Security Token Service APIs are **not enabled** yet. That's step A.

### Decisions
- **DQ rule ownership (the user's point):** data quality rules should be **written by data stewards, with the data owner's approval**, because they are closest to the data and its use. The 23 rules in `dq_rules.csv` are **drafts proposed by the governance hub**, pending each domain's sign-off. The hub owns the framework (catalog, findings, scorecard, controls); the domains own the rule content.
- **Leaning toward a federated (hub-and-spoke) governance model** over a centralized one. The hub (Data Governance Manager) sets standards, tooling, the scorecard and reporting. Domain owners and stewards (the spokes) make and enforce decisions for their data. Roles and responsibilities to be fleshed out (backlog).
- **Keyless sign-in** (Workload Identity Federation): restricted to this repository by an attribute condition; one service account, `ect-pipeline`.
- **Least privilege:** BigQuery Job User (project) plus BigQuery Data Editor on `raw`, `staging` and `marts` only. No service-account key is ever created.
- **Catch-up design:** the pipeline works out what's missing from BigQuery itself rather than trusting the schedule, so missed days heal themselves.
- **Run records are committed to the repo:** audit evidence for each run (Project 3 control monitoring), and the commits keep GitHub from pausing the schedule after 60 days of inactivity. **Open question:** commit them straight to `main`, which needs the user's OK, or to a separate branch.

- Pushing the workflow needed the GitHub CLI's `workflow` permission. The user granted it with `gh auth refresh -s workflow`; in `!` commands use the full path `/opt/homebrew/bin/gh`.
- **The user completed console setup steps A–F.** Merged `daily-refresh` to `main` from the CLI at the user's request. Run records go to `main` by default, since the user hasn't chosen otherwise.

- **First run failed (403 `iam.serviceAccounts.getAccessToken`).** Cause: in the provider's attribute mapping, the OIDC side read `attribute.repository` instead of `assertion.repository` (same for `repository_owner`), so the step E impersonation grant never matched. Found with read-only `gcloud` checks; **the user fixed it in the console.**
- **Re-run:** sign-in, catch-up, load and `dbt build` all **succeeded**. Only the run-record push failed, because `main` had moved ahead (the first run had committed its own failure record). **Fixed:** the workflow now rebases before pushing, and records are named `<date>_<time>.md` so same-day runs never clash.

- Merged `run-record-fix` to `main` from the CLI at the user's request (`1ff4423`).
- **First fully green run** (run 45425307173, manual, 1m35s): 9 generator tests passed; catch-up found 2026-11-23 loaded (0 days due); dbt 91 pass, 23 warn, 0 errors; run record `run-records/2026-11-24_1026.md` committed by the bot (`93216de`).

### Next steps
1. Check tomorrow's scheduled run (05:30 New York), the first to load a new day (2026-11-24).

---

## 2026-11-24 — Marts, rule catalog and data-quality scorecard

### Done
- Merged `dbt-project` to `main` from the CLI at the user's request (`e412f30`).
- **Answered the user's questions:**
  - *Where are the reference rules?* Before this step there was only REF-01, a staging test. Now **all rules live in one catalog** (`seeds/dq_rules.csv`, 23 rules): DQ-01 to DQ-16 (planted), T1 to T4 (real trip data), REF-01 to REF-03 (reference data).
  - *How is `gov_planted_defects` used?* As the **answer key** for scoring the checks. `fct_dq_scorecard` compares the findings with it per record.
- **Rule logic in one place:** `marts.fct_dq_findings` lists every failing record (rule, table, record ID, column; never values). One dbt test per rule warns when there are findings. The old per-column DQ tests in staging were removed.
- **Scorecard** `marts.fct_dq_scorecard`: **100% detection on all 16 planted rules and 0 false positives**, scored record by record. Real-data findings: T1 2,492, T2 19,306, T3 5,011, T4 138, REF-01 2, REF-02 4,993, REF-03 3,879.
- **Two governance controls run on every build:**
  - `scorecard_every_planted_defect_caught` (error if a rule misses any planted defect);
  - `assert_marts_classification_cap` (error if a marts table is labeled above Sensitive, or has a Secret/Confidential column). **Both pass.**
- **14 marts tables** in `marts`, all labeled (layer `marts`, classification sensitive / internal / public):
  - Dimensions: `dim_employees`, `dim_drivers`, `dim_riders`, `dim_rider_cards`, `dim_taxi_zones`, `dim_campaigns`, `dim_rider_segments`, `dim_dq_rules`.
  - Facts: `fct_trips` (357k, partitioned by pickup date, clustered by driver), `fct_daily_zone_trips` (24.6k), `fct_trip_surveys`, `fct_ledger_entries`, `fct_dq_findings` (37.1k), `fct_dq_scorecard`.
- Full build: **114 nodes; 91 pass, 23 warn (the rules), 0 errors.** The heaviest query processed 75 MB.

### Decisions
- **How the Sensitive cap is applied in marts:**
  - **Removed:** SSN, bank account, card number, expiry and cardholder (Secret); salary, rating, contact details, licence, background check (Confidential).
  - **Masked:** card number → last 4 digits; survey comment → phone numbers and emails `[REDACTED]`.
  - **Generalized:** in `fct_trips`, pickup and dropoff zone → **borough**, because zone plus rider_id would reveal a person's movements. Zone-level demand is in `fct_daily_zone_trips`, aggregated with no rider or driver IDs.
- **`dim_rider_cards` is out of PCI scope** (last 4 digits only), so it's labeled `pci_scope: false`.
- **Reference data is corrected in marts, not staging.** `dim_taxi_zones` collapses duplicate IDs and adds zones 57, 104, 105, 264 and 265 from a documented supplement seed (`zone_source` shows which). Staging keeps the public data as published, so REF-01 stays visible.
- **Duplicate rules flag only the later copies** (by ID order), not the first holder of a value. That matches how the defect arises.
- **T5 dropped** (total ≠ components): the public table lacks the congestion surcharge, so it would flag almost every trip. T6 (bad driver/rider IDs) is now covered by the relationship tests.
- Marts are full-rebuild tables for now (small data). Switch `fct_trips` to incremental if build cost grows.

### Next steps
- GitHub Actions daily run (generate → load → `dbt build`), which needs a Workload Identity setup by the user in the console.
- Looker Studio: a DQ scorecard and trips dashboard on `marts`.

---

## 2026-11-24 — dbt project: staging layer and data-quality tests

### Done
- Merged `bulk-backfill` to `main` from the CLI at the user's request (`7c4b94e`).
- Built **`data-platform/dbt/`** (dbt 1.12, BigQuery). It uses the user's Google sign-in with no keys, a 1 GB cap per query, and job labels for cost tracing.
  - **16 staging views** in `staging`:
    - a current-version view (`stg_*`) for each raw table;
    - full-history views (`stg_*_history`, with `valid_from`, `valid_to`, `is_current`) for employees, drivers, riders, cards and segments;
    - trips, surveys, ledger, taxi zones, and the answer key.
  - Each view carries its description and **10 labels** (layer `staging`).
  - **Tests:**
    - 42 structural tests (unique IDs, plus links between tables: trips→drivers, drivers→HR, cards→riders, campaigns→segments). **All pass.**
    - The **16 data-quality rules DQ-01 to DQ-16**, as warnings. DQ-13 to DQ-16 are new, so every planted defect type has a rule.
  - **Freshness checks** on the daily-changing raw tables (warn after 2 days without a load, error after 4).
- **First scorecard:** every rule catches exactly the number planted, with no false positives. Uniqueness and allowed-values rules count distinct values rather than rows. The table is in `data-quality-rules.md`.
- **Verified history:** 647 employees and 470 drivers, each with exactly one current version. DRV10200 shows active → suspended → reinstated → inactive.

### Decisions
- **Revised:** history comes from **`raw` change logs** through dbt views, **not dbt snapshots**. Raw already stores every version, so history covers 2026-01-01 onward and can be rebuilt. Snapshots would only start recording from their first run and couldn't be rebuilt. Snapshots stay available for sources that aren't change logs.
- **Staging keeps defects as they are:** no clean-up, so the tests can find problems. Fixes happen only after an owner or council decision, which makes the remediation demo.
- **Data-quality rules are warnings, not failures.** Structural tests are errors.
- **dbt writes only to existing datasets** (`staging`, later `marts`). A schema-name macro stops dbt from creating new datasets.
- Staging is views, not tables: no storage cost, and always up to date with `raw`.

### Real-data findings (not planted)
- **REF-01:** the public taxi zone table has duplicate IDs. Zone 57 (Corona) is filed under 56, and 104/105 (the harbor islands) under 103. This explains why zone 57 trips have no match.

### Next steps
- Marts (`dim_*`, `fct_*`, capped at Sensitive) and a per-record DQ scorecard; or the GitHub Actions daily run.

---

## 2026-11-24 — Backfill loaded into BigQuery `raw`

### Done
- Merged `tlc-december-fix` to `main` from the CLI at the user's request (`5088859`).
- Added **bulk backfill** to the loader (`--bulk`): one load job per table for a whole date range, instead of one job per table per day (~2,300 jobs). It refuses to run if any of those days is already loaded, and it checks row counts.
- **Loaded 2026-01-01 → 2026-11-23** in about 1.5 minutes (loads are free). All 10 tables were created with their descriptions and 10 labels each, partitioned by `_batch_date`:

  | Table | Rows |
  |---|---|
  | `app_trips` | 357,049 (91 MB) |
  | `app_trip_surveys` | 10,908 |
  | `app_riders` | 4,645 |
  | `payments_rider_cards` | 3,894 |
  | `gov_planted_defects` | 1,237 |
  | `hris_employees` | 954 |
  | `fleet_drivers` | 783 |
  | `payments_financial_ledger` | 204 |
  | `app_rider_segments` | 132 |
  | `app_marketing_campaigns` | 62 |

- **Verified:**
  - Every row count matches the generator's manifests.
  - All 12 `raw` tables carry 10 labels.
  - **Re-loading 2026-11-23 left it at 1,090 trips**, so re-runs replace rather than duplicate.
  - Trip IDs are unique.

### Real-data findings (not planted)
- **5,000 trips have pickup zones that aren't in the zone reference table:** 264 "Unknown" (4,199), 265 "Outside NYC" (792), and zone 57 (2). That's a genuine reference-data gap, good material for a referential-integrity check and a reference-data issue.

### Risks / watch items
- Storage usage per table (`INFORMATION_SCHEMA.TABLE_STORAGE`) needs an extra permission the user's account doesn't have. Table details in the console show the sizes anyway.

### Next steps
- Suggested order: (1) dbt project (staging models and snapshots over `raw`), (2) GitHub Actions daily run, (3) column descriptions and the gap register, (4) Phase 1 tables.

---

## 2026-11-24 — TLC setup run; December gap fixed; backfill generated

### Done
- **The user ran `sql/01` and `sql/02` in the BigQuery console.** Verified read-only:
  - `raw.tlc_yellow_trips_sample`: **362,834 trips**, 76 MB, partitioned by day, 10 labels, no duplicate keys.
  - `raw.tlc_taxi_zones`: 263 zones, 10 labels.
- **Found:** the public 2022 table stops on **2022-11-30** (no December). **Fixed:** simulated dates that land in December now replay the trips from 5 weeks earlier, on the same weekday. The test now checks every day for two years.
- **Generated the backfill locally:** 2026-01-01 → 2026-11-23 (327 days). It contains 357,049 trips, 10,908 surveys, 4,645 rider records, 3,894 card records, 954 HR records, 783 fleet records, and 1,237 planted defects. Nothing is loaded yet.
- Checked a spurious alarm: every `tlc_sample_key` ends in "00". That is expected, because the 1% sample keeps only trips whose hash is divisible by 100.

### Real-data findings (not planted; future data-quality material)
- **2022-09-18 has only 36 trips** (normal is ~1,100), an apparent gap in the public data. It is replayed as **2026-09-13**, which makes a good test for a volume anomaly check.
- **2022-01-29 is low (339)** because of the real blizzard. That's a true dip, not an error.

### Next steps
- The user approves the backfill load into `raw` (loads are free).

---

## 2026-11-24 — Phase 0: daily data generator and loader

### Done
- Merged `project-context` (CLAUDE.md, public WORKLOG) to `main` from the CLI at the user's request (`fc55a41`).
- Built **`data-platform/`**: a Python package (uv, Python 3.12, Faker 37) with a generator, a loader, one-time SQL and tests.
  - **Generator** (`uv run ect-generate`): replays company life from **2026-01-01** day by day, and writes each day's new and changed records to `output/<date>/*.jsonl` with a manifest (row counts, SHA-256).
  - **Lifecycle:** hires and terminations; driver onboarding → background check → active; suspensions and reinstatements; a March 1 annual review; rider sign-ups, profile changes and closures; cards added and removed; new campaigns; monthly segment refresh; ledger postings on the 3rd.
  - **Drivers are now employees**, so every `DRV` has an `EMP` in HR. That is the foundation for GV-004 (terminated in HR, still active in fleet), which gets planted in Phase 3.
  - **Trips:** about 1,000 real 2022 NYC yellow-taxi trips a day, replayed on the same weekday (52-week cycle). Synthetic drivers are assigned; riders only on app-booked card trips, while street hails have no rider. Surveys go on about 6% of app trips.
  - **Planted defects:** the 16 Project 1 defect types carry over. Every one is logged in the answer key `gov_planted_defects` (record and column only, never the bad value). The epoch batch plants 292.
  - **Loader** (`uv run ect-load`): creates each `raw` table on first load with its schema, description and labels. Tables are partitioned by `_batch_date`, and each day replaces only its own partition, so history is append-only and re-runs can't duplicate.
  - **One-time SQL** (validated with dry runs; **not run yet**): `sql/01` copies a fixed 1% sample of 2022 TLC trips (~6.8 GB scan, ~360k rows), and `sql/02` copies the 263 taxi zones (~2 MB).
  - **Tests:** 9 passing. They cover same date → identical data, byte-identical files, weekday-aligned TLC mapping, prefixed IDs, trips only to active drivers, schema and label coverage, Luhn-valid cards, and an answer key with no values.
- Checked the simulated state on 2026-11-23: 331 active drivers, 494 active employees, 3,714 active riders, 3,385 active cards, 0 HR/fleet mismatches.

### Decisions
- **2023 TLC data is not usable.** The public 2023 table is empty, so 2022 is replayed in a 52-week cycle that keeps weekdays aligned. Trips repeat yearly, but driver and rider assignments differ.
- **Replay-from-start design:** state on any date is rebuilt from 2026-01-01 (under 1 second for a year), so no state files need storing. The trade-off is that changing generator code changes history; `_generator_version` on every row traces which code made it.
- **Incremental extracts:** raw holds full record images each time a record changes, not just events. That is the standard input for dbt snapshots.
- **Code lives in `data-platform/`** at the repo root, because it serves all four projects. The Project 1 generator and CSVs stay as they are, as Project 1 artifacts.
- **The answer key goes in the warehouse** (`raw.gov_planted_defects`), so a data-quality scorecard (caught vs. planted) can run in SQL. Checks must not read it.
- **Safe synthetic values:** 555 phone numbers, reserved email domains, a test-style `4000 00` card prefix. Card numbers are Luhn-valid, so Google Sensitive Data Protection will recognise them.
- Labels are applied when the loader creates each raw table (part of the "labels on tables" backlog item). Planted label gaps are still to come.

### Risks / watch items
- `trip_distance`, fares and other TLC values pass through untouched, including the real data's errors. That is intended.
- The epoch batch is about 4,900 records; later days are a few dozen records plus about 1,000 trips.

- Committed as `629742a` on branch `phase-0-generator`; **merged to `main` from the CLI** at the user's request.
- The user chose to **run the one-time SQL themselves in the BigQuery console**.

### Next steps
1. The user runs `sql/01` and `sql/02` in the BigQuery console (one-time; ~6.8 GB scanned).
2. Backfill: `ect-generate --backfill`, then `ect-load` for 2026-01-01 → yesterday.
3. Check the tables in the BigQuery console.

---

## 2026-11-23 — Governance org and council charter; repo housekeeping

### Done
- **Org structure** (`01-governance-program/governance/governance-org-structure.md`): reporting lines, fictional named role holders, owners and stewards per domain, custodian and consumer roles, and the department objectives that create governance tensions.
- **Council charter** (`01-governance-program/governance/data-governance-council-charter.md`): purpose, authority, membership and voting, meetings and quorum, decision rules, issue lifecycle with severity targets, escalation path, a RACI for 12 decision types, standing agenda, 7 KPIs, and the initial backlog GV-001 to GV-006, each tied to a defect planted in the data.
- Committed as `245c3e7` on branch `governance-council`; **merged to `main` from the CLI** at the user's request.
- Added `CLAUDE.md` (project context and working agreements) and moved this log into the repo as `WORKLOG.md`. The user chose to keep the log **public**. Committed as `8fe21bb` on branch `project-context`; **merged to `main` from the CLI** at the user's request.

### Decisions
- Council members get **fictional names**. Names appear in docs and minutes only; labels and data use role slugs.
- **The CDO (Renée Okonkwo) is the final escalation point**, as leader of the data organization. Vetoes and deadlocks go to the CDO, and the CEO receives a quarterly governance report.
- The **CISO and Privacy Officer keep their vetoes**. The Privacy Officer reports to General Counsel, which keeps privacy independent of the CDO.

---

## 2026-11-23 — Classification, labels, dataset layout

### Done
- **Label standard** (`01-governance-program/governance/labeling-standard.md`, v0.1): label keys for datasets and tables, a domain register, formatting rules, a planned automated compliance check, and deliberate label gaps.
- **Dataset labels** applied by the user in the console (`layer`, `classification`, `data_custodian`, `environment`, `managed_by`) and confirmed with a read-only check.
- **Datasets** `raw`, `staging` and `marts` created by the user (US location, no table expiry), with descriptions. Ownership is carried by labels, not descriptions.
- Committed as `f403b0f` (branch `five-tier-classification`) and **merged to `main`** with the user's approval.

### Decisions
- **Five-tier classification: Secret → Confidential → Sensitive → Internal → Public**, replacing Restricted → Confidential → Internal → Public. The user chose "Internal" over "Restricted" for tier 4, because "Restricted" usually signals a high tier. **SSN = Secret.**
  - **Secret:** SSN, cardholder data (card number, expiry, name), payout bank account, credentials.
  - **Confidential:** contact PII, TLC license, background check, salary, performance rating, pickup/dropoff locations, free-text comments.
  - **Sensitive:** names, employee work email, fares/tips/totals, ledger amounts, budgets.
  - Column map: 6 Secret, 12 Confidential, 12 Sensitive, 38 Internal, 1 Public.
  - Handling: Secret never goes to non-prod or `marts`. Confidential is masked or aggregated in `marts`. **`marts` is capped at Sensitive.**
  - Applied across 15 files. The vendor-risk tool keeps its 1–4 scoring, with the option labels updated.
  - Also fixed a glossary CSV bug: unquoted commas would have broken the catalog import.
- **Dataset layout: by layer** (`raw` / `staging` / `marts`). The domain is carried by labels. Raw tables get a source-system prefix (`hris_`, `fleet_`, `payments_`, `app_`, `tlc_`). dbt names its tables `stg_*` in staging and `dim_*`/`fct_*` in marts. Access control is set per layer (analysts get `marts` only).
- **Prefixed IDs** (`DRV10042`, `EMP10001`, `RDR…`, `VEH…`) replace integer IDs.

### Design review of the ChatGPT notes (tables, lifecycle, org, council)
- Adopted: department conflicts and the governance council; lifecycle data (hires, terminations, reassignments, no physical deletes); staged rollout; taxi data treated as one source system among several.
- Adjusted:
  - **`raw` is append-only.** History tables come from **dbt snapshots**, not UPDATEs to BigQuery.
  - **The daily generator is deterministic code** run by GitHub Actions, not Claude-in-the-loop. Claude/MCP write access is a gated Project 4 item.
  - **Governance records are repo files loaded as dbt seeds.**
  - **Real TLC taxi zones** are used for locations.
  - **Project 2's control matrix** is reused as `compliance_controls`.
- **Rule:** every conflict scenario is backed by a defect planted in the data.
- **Phased table plan:**

  | Phase | Scope |
  |---|---|
  | 0 | Framework and the existing tables |
  | 1 | `vehicles`, `vehicle_assignments`, `payment_transactions`, `driver_payouts`, org seeds |
  | 2 | `rider_consent`, `support_tickets`, `privacy_requests`, `data_access_logs` |
  | 3 | Council scenarios |
  | 4 | Clickstream (nested `app_events`) |

---

## 2026-11-23 — Tools, sign-ins, Google Cloud guardrails

### Done
- Installed:
  - Homebrew (by the user)
  - gh 2.105.0
  - uv 0.13.9 and Python 3.12
  - Google Cloud CLI 594.0.1
  - dbt-core 1.12.7 with dbt-bigquery 1.12.4
- Signed in to GitHub CLI (`2Wake`), gcloud, and application-default credentials.
- Fixed `command not found: gh`: added Homebrew's setup line to `~/.zshrc`.
- Cloned the repo to `~/empire-city-taxi-grc`. The repo's git identity uses the GitHub noreply email, so no personal email appears in commits.
- Google Cloud project **`empire-city-taxi`** (billing enabled) set as the default.
- **Cost guardrails:**
  - Budget **"ECT free-tier guardrail"**: $5/month, alerts at 5¢, $1, $2.50 and $5 actual, plus a forecast alert. Created by Claude through the CLI, before the UI-only agreement.
  - **BigQuery "Query usage per day" quota set to 0.03 TiB (~30 GB)** by the user in the console. This hard cap keeps a month of queries under the 1 TB free tier.
  - `maximum_bytes_billed` per query (in dbt) and date-partitioned tables are still to come.

### Working agreements established
- The user makes all cloud and account configuration changes **in the web UI**. Claude provides the steps and changes no settings without explicit approval.
- Commits go on a branch. **Claude always asks before merging anything.**
- Every step is logged here.

---

## 2026-11-23 — Migrated from Claude Chat to Claude Code; stack decided

### Done
- Brought the Claude Chat build log (Projects 1 and 2 complete, Projects 3 and 4 planned) into Claude Code.
- Connected the GitHub MCP. It's read-only, so writes go through `gh`.
- Checked the laptop: 8 GB RAM, which rules out running OpenMetadata, Airflow and Metabase locally.

### Decisions

| Area | Decision | Rationale |
|---|---|---|
| Warehouse | **BigQuery with billing on** (not the sandbox) | Removes the sandbox's 60-day table expiry. About 2–3 GB/yr expected, against 10 GB of free storage. |
| Cost control | Daily query quota, per-query byte limit, budget alerts, partitioning | The quota and per-query limits block spending; alerts only warn. |
| Catalog / governance | **Collate free tier** (hosted OpenMetadata) | Uses no laptop RAM. |
| Orchestration | **GitHub Actions** daily, keyless login through Workload Identity Federation | Free, runs off the laptop. Cloud Composer costs hundreds of dollars a month. Each run's committed record doubles as control evidence. |
| Transform / DQ | **dbt Core**; the full DQ rule set runs daily in dbt | Free within the BigQuery free tier. Collate's free tier allows only 10 tests. |
| PII detection | Google Sensitive Data Protection (sampled one-off jobs) plus manual tags checked against the answer key | Collate's PII auto-classification is paid only. SDP's first 1 GB/month is free. |
| Reporting | Looker Studio | Free, in the cloud. |
| Avoid | Cloud Composer, Cloud SQL, scheduled Dataplex DQ scans | Cost. Dataplex DQ isn't in the free tier or covered by the BigQuery quota. |

### Risks / watch items
- **Collate's free tier is reclaimed after 4 weeks without a login.** Log in every couple of weeks, and keep the governance artifacts in the repo as the backup.
- Collate free-tier limits: 5 users, 500 assets, weekly refresh and tests, 10 test cases, 5 alerts.
- Collate's AI behavior is undocumented (on by default? auto-applied? which LLM?). Evaluate it after sign-up; possible Project 4 material.
- GitHub pauses scheduled workflows in public repos after 60 days without activity. The daily run-record commit keeps the repo active.
- Collate reads BigQuery through a read-only service-account key. Record it in the vendor-risk tool.
