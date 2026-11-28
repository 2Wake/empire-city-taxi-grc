"""Tests for the daily security review and the watchdog, on made-up log entries (no Google access)."""
import json
from datetime import date, datetime, timedelta

from ect_platform import security_review as sr
from ect_platform import watchdog as wd

PIPE = "ect-pipeline@empire-city-taxi.iam.gserviceaccount.com"
ANALYST = "ect-role-analyst@empire-city-taxi.iam.gserviceaccount.com"
OWNER = "someone.personal@gmail.com"
WORKFLOW = "repo:2Wake@328668218/empire-city-taxi-grc@1469202513:ref:refs/heads/main"
POOL = "principal://iam.googleapis.com/projects/1/locations/global/workloadIdentityPools/github/subject/"
IDS = sr.load_identities(OWNER)


def entry(method, who=PIPE, service="bigquery.googleapis.com", resource="", ts="2026-11-24T10:00:00.123456789Z",
          code=0, subject=None, **extra):
    auth = {"principalEmail": who} if who else {}
    if subject:
        auth["principalSubject"] = subject
    p = {"methodName": method, "serviceName": service, "resourceName": resource, "authenticationInfo": auth}
    if code:
        p["status"] = {"code": code}
    p.update(extra)
    return {"timestamp": ts, "protoPayload": p}


def kinds(alerts):
    return sorted(a["alert"] for a in alerts)


# ---- Admin Activity ----

def test_admin_alerts():
    entries = [
        entry("SetIamPolicy", OWNER, "cloudresourcemanager.googleapis.com", "projects/empire-city-taxi"),
        entry("SetIamPolicy", OWNER, "cloudresourcemanager.googleapis.com", "projects/empire-city-taxi",
              request={"updateMask": "auditConfigs"}),
        entry("google.iam.admin.v1.CreateServiceAccountKey", OWNER, "iam.googleapis.com",
              "projects/empire-city-taxi/serviceAccounts/ect-pipeline@x/keys/1"),
        entry("google.logging.v2.ConfigServiceV2.UpdateBucket", OWNER, "logging.googleapis.com"),
        entry("google.cloud.bigquery.v2.DatasetService.UpdateDataset", OWNER,
              resource="projects/empire-city-taxi/datasets/raw"),
    ]
    assert kinds(sr.check_admin(entries, IDS)) == ["IAM_CHANGED", "IAM_CHANGED", "LOGGING_CHANGED",
                                                   "LOGGING_CHANGED", "SA_KEY_CREATED"]


def test_admin_ignores_failed_and_legacy_duplicates():
    entries = [
        entry("SetIamPolicy", OWNER, "cloudresourcemanager.googleapis.com", code=7),
        entry("datasetservice.update", OWNER, resource="projects/empire-city-taxi/datasets/raw"),
    ]
    assert sr.check_admin(entries, IDS) == []


# ---- raw reads ----

def read(who, table="hris_employees"):
    return entry("google.cloud.bigquery.v2.JobService.InsertJob", who,
                 resource=f"projects/empire-city-taxi/datasets/raw/tables/{table}",
                 metadata={"tableDataRead": {"reason": "JOB"}})


def test_raw_reads_follow_access_matrix():
    allowed = sr.raw_roles()
    assert {"platform_admin", "security_analyst"} <= allowed and "data_analyst" not in allowed
    alerts = sr.check_raw_reads([read(PIPE), read(OWNER), read(ANALYST), read("stranger@gmail.com")], IDS, allowed)
    assert [(a["identity"], a["detail"]) for a in alerts] == [
        ("ect-role-analyst", "raw.hris_employees"),
        (f"unknown-identity-{sr._hash('stranger@gmail.com')}", "raw.hris_employees")]


def test_reads_outside_raw_ignored():
    e = read(ANALYST)
    e["protoPayload"]["resourceName"] = "projects/empire-city-taxi/datasets/marts/tables/dim_employees"
    assert sr.check_raw_reads([e], IDS, sr.raw_roles()) == []


# ---- denials ----

def test_denials_sliding_window():
    base = datetime(2026, 11, 24, 10, 0)
    def at(minutes):
        return (base + timedelta(minutes=minutes)).isoformat() + "Z"
    four = [entry("x", ANALYST, ts=at(m), code=7) for m in (0, 10, 20, 30)]
    assert sr.check_denials(four, IDS) == []
    spread = four + [entry("x", ANALYST, ts=at(95), code=7)]  # 5 in the day, but not within 1 hour
    assert sr.check_denials(spread, IDS) == []
    five = four + [entry("x", ANALYST, ts=at(55), code=7)]
    alerts = sr.check_denials(five, IDS)
    assert kinds(alerts) == ["ACCESS_DENIALS"] and alerts[0]["count"] == 5


# ---- sign-ins ----

def test_signins():
    good_sts = entry("google.identity.sts.v1.SecurityTokenService.ExchangeToken", None, "sts.googleapis.com",
                     subject=WORKFLOW)
    branch_sts = entry("google.identity.sts.v1.SecurityTokenService.ExchangeToken", None, "sts.googleapis.com",
                       subject=WORKFLOW.replace("refs/heads/main", "refs/heads/evil"))
    gat = lambda caller, target=PIPE, subject=None: entry(  # noqa: E731
        "GenerateAccessToken", caller, "iamcredentials.googleapis.com", subject=subject,
        request={"name": f"projects/-/serviceAccounts/{target}"})
    entries = [good_sts, branch_sts,
               gat(None, subject=POOL + WORKFLOW),   # the workflow becoming ect-pipeline: fine
               gat(PIPE),                            # ect-pipeline refreshing its own token: fine
               gat(PIPE, target=ANALYST),            # the access check acting as a role account: fine
               gat(OWNER)]                           # a person impersonating ect-pipeline: alert
    alerts = sr.check_signins(entries, IDS)
    assert kinds(alerts) == ["PIPELINE_SIGNIN", "PIPELINE_SIGNIN"]
    assert {a["identity"] for a in alerts} >= {"maintainer"}


# ---- access check findings ----

def test_access_findings_new_or_increased_only():
    alerts, known = sr.check_access_findings({"acc_01": 4, "acc_02": 3, "acc_11": 1},
                                             {"acc_01": 4, "acc_02": 2})
    assert [a["detail"] for a in alerts] == ["`acc_02` (up from 2)", "`acc_11` (new)"]
    assert known == [{"test": "acc_01", "count": 4, "previous": 4}]


def test_record_parsing():
    text = ("- Reviewed through: 2026-11-24\n\n| Check | Status | Failing records |\n|---|---|---|\n"
            "| `acc_01_iam_access_grants_dataset` | warn | 4 |\n| `dq_04_x` | warn | 9 |\n")
    assert sr.acc_counts_from_record(text) == {"acc_01_iam_access_grants_dataset": 4}
    assert sr.reviewed_through(text) == date(2026, 11, 24)


def test_days_to_review_catches_up():
    today = date(2026, 11, 27)
    assert sr.days_to_review(None, today) == ([date(2026, 11, 26)], 0)
    assert sr.days_to_review(date(2026, 11, 24), today) == ([date(2026, 11, 25), date(2026, 11, 26)], 0)
    assert sr.days_to_review(date(2026, 11, 26), today) == ([], 0)
    days, skipped = sr.days_to_review(date(2026, 11, 1), today)
    assert len(days) == 7 and skipped == 18 and days[-1] == date(2026, 11, 26)


# ---- privacy and the record ----

def test_display_never_shows_personal_email():
    assert sr.display(OWNER, IDS) == "maintainer"
    assert "@" not in sr.display("other.person@gmail.com", IDS)
    assert sr.display("bqsystbl@system.gserviceaccount.com", IDS) == "google-system-account"
    assert sr.display(POOL + WORKFLOW, IDS) == "github-workflow (main)"


def test_record_and_check(tmp_path):
    path = tmp_path / "r.json"
    result = {"status": "ok", "days": ["2026-11-24"], "reviewed_through": "2026-11-24", "skipped_days": 0, "entries_checked": {"admin": 3},
              "notes": [], "known_findings": [],
              "alerts": [sr._alert("IAM_CHANGED", "maintainer", 1, "SetIamPolicy on project", "2026-11-24T10:00:00Z")]}
    path.write_text(json.dumps(result))
    text = "\n".join(sr.record_lines(path))
    assert "- Reviewed through: 2026-11-24" in text and "maintainer" in text and "@" not in text
    assert sr.check_result(path) == 1
    result["alerts"] = []
    path.write_text(json.dumps(result))
    assert sr.check_result(path) == 0
    result["status"] = "not_run"
    path.write_text(json.dumps(result))
    assert sr.check_result(path) == 1
    assert sr.check_result(tmp_path / "missing.json") == 1


# ---- watchdog ----

def test_watchdog(tmp_path):
    winter_noon = datetime(2026, 12, 2, 12, 5, tzinfo=wd.NY)
    assert wd.evaluate(winter_noon, "5 16 * * *", tmp_path)[0] == 0        # summer cron in winter: skip
    code, msg = wd.evaluate(winter_noon, "5 17 * * *", tmp_path)
    assert code == 1 and "SEV3" in msg                                     # today and yesterday missing
    (tmp_path / "2026-12-01.md").write_text("x")
    code, msg = wd.evaluate(winter_noon, None, tmp_path)
    assert code == 1 and "SEV4" in msg                                     # only today missing
    (tmp_path / "2026-12-02_0531.md").write_text("x")
    assert wd.evaluate(winter_noon, None, tmp_path)[0] == 0
    assert wd.evaluate(datetime(2026, 12, 3, 9, 0, tzinfo=wd.NY), None, tmp_path)[0] == 0  # before noon
    summer_noon = datetime(2027, 7, 1, 12, 5, tzinfo=wd.NY)
    assert wd.evaluate(summer_noon, "5 17 * * *", tmp_path)[0] == 0        # winter cron in summer: skip
    assert wd.evaluate(summer_noon, "5 16 * * *", tmp_path)[0] == 1


def test_latest_looks_past_records_without_a_value():
    records = ["# newest: reviewed no days, dbt failed", "- Reviewed through: 2026-11-23\n| `acc_01` | warn | 4 |"]
    assert sr.latest(records, sr.reviewed_through) == date(2026, 11, 23)
    assert sr.latest(records, sr.acc_counts_from_record) == {"acc_01": 4}
    assert sr.latest(["nothing here"], sr.reviewed_through) is None


def test_service_account_iam_changes_any_casing():
    # The IAM service logs SetIAMPolicy (capital IAM); missed on 2026-11-25 (GOV-169).
    e = entry("google.iam.admin.v1.SetIAMPolicy", OWNER, "iam.googleapis.com",
              "projects/empire-city-taxi/serviceAccounts/104223270256367818744")
    alerts = sr.check_admin([e], IDS)
    assert kinds(alerts) == ["IAM_CHANGED"] and alerts[0]["identity"] == "maintainer"


def test_iam_alert_says_what_changed():
    # 2026-11-27: two alerts said only "SetIamPolicy on project", with no date or change (owner feedback).
    deltas = {"bindingDeltas": [
        {"action": "ADD", "role": "roles/bigquery.jobUser", "member": "serviceAccount:ect-watchdog@empire-city-taxi.iam.gserviceaccount.com"},
        {"action": "ADD", "role": "roles/bigquery.metadataViewer", "member": "serviceAccount:ect-watchdog@empire-city-taxi.iam.gserviceaccount.com"},
        {"action": "REMOVE", "role": "roles/viewer", "member": "user:" + OWNER},
        {"action": "ADD", "role": "roles/bigquerydatatransfer.serviceAgent",
         "member": "serviceAccount:service-722503408036@gcp-sa-bigquerydatatransfer.iam.gserviceaccount.com"}]}
    e = entry("SetIamPolicy", OWNER, "cloudresourcemanager.googleapis.com", "projects/empire-city-taxi",
              ts="2026-11-27T09:23:10.289847Z", serviceData={"policyDelta": deltas})
    [a] = sr.check_admin([e], IDS)
    assert a["detail"] == ("SetIamPolicy on project: added bigquery.jobUser, bigquery.metadataViewer to ect-watchdog; "
                           "added bigquerydatatransfer.serviceAgent to google-service-agent (bigquerydatatransfer); "
                           "removed viewer from maintainer")
    assert "@" not in a["detail"] and "722503408036" not in a["detail"]
    text = "\n".join(sr.check_lines({"days": ["2026-11-26", "2026-11-27"], "alerts": [a]}, "data-platform/run-records/x.md"))
    assert "Security review of 2026-11-26 to 2026-11-27 (UTC): 1 alert to triage." in text
    assert "When:   2026-11-27 09:23 UTC (04:23 New York)" in text
    assert "Who:    maintainer" in text and "How to triage" in text and "x.md" in text


def test_check_writes_github_summary(tmp_path, monkeypatch):
    path, summary = tmp_path / "r.json", tmp_path / "summary.md"
    path.write_text(json.dumps({"status": "ok", "days": ["2026-11-27"], "notes": [], "alerts": [
        sr._alert("IAM_CHANGED", "maintainer", 2, "SetIamPolicy on project", "2026-11-27T09:23:10Z")]}))
    monkeypatch.setenv("GITHUB_STEP_SUMMARY", str(summary))
    assert sr.check_result(path, tmp_path) == 1
    assert "| 1 | SEV3" in summary.read_text() and "2026-11-27 09:23 UTC (04:23 New York)" in summary.read_text()


# ---- policy acknowledgment summary ----

def test_ack_summary_lines_and_final_count(tmp_path, monkeypatch):
    from ect_platform import acknowledgments as ack
    counts = {"people": 527, "done": 472, "overdue": 55, "done_on_day": 25, "acks_required": 8432,
              "acks_done": 7600, "next_due": date(2026, 12, 14),
              "deadlines_today": [{"due_on": date(2026, 12, 9), "people": 524, "met": 470}]}
    s = ack.summarize(counts, date(2026, 12, 9))
    assert s["lines"][0] == "472 of 527 people have acknowledged everything (90%). 55 still to go."
    assert s["final_lines"] == ["Deadline Wednesday, December 9, 2026 has passed: 470 of 524 people due that day met it (90%); 54 did not."]
    html = ack.comment_html(s)
    assert "[Simulated]" in html and "Acknowledgment update for Wednesday, December 9, 2026" in html
    monkeypatch.delenv("CONFLUENCE_USER", raising=False)
    assert ack.post(s).startswith("Not posted")
    path = tmp_path / "a.json"
    path.write_text(json.dumps({**s, "posted": "Not posted"}, default=str))
    text = "\n".join(ack.record_lines(path))
    assert "- People: 472 of 527 done, 55 left, 55 overdue" in text and "- Final: Deadline" in text
    assert "Not counted" in "\n".join(ack.record_lines(tmp_path / "missing.json"))


# ---- configuration check ----

def test_config_check_rules():
    from ect_platform import config_check as cc
    policy = {"bindings": [
        {"role": "roles/owner", "members": ["user:" + OWNER]},
        {"role": "roles/editor", "members": ["user:stranger@example.com"]},
        {"role": "roles/logging.privateLogViewer", "members": ["serviceAccount:ect-monitor@empire-city-taxi.iam.gserviceaccount.com"]}],
        "auditConfigs": [{"service": "iam.googleapis.com", "auditLogConfigs": [{"logType": t} for t in ("ADMIN_READ", "DATA_READ", "DATA_WRITE")]}]}
    r = {x["check"][:6]: x for x in cc.check_iam(policy, IDS)}
    assert r["CFG-01"]["status"] == "finding" and "roles/editor" in r["CFG-01"]["detail"]
    assert r["CFG-02"]["status"] == "finding" and "@" not in r["CFG-02"]["detail"]
    assert r["CFG-03"]["status"] == "finding" and "sts" in r["CFG-03"]["detail"]
    assert cc.check_keys([{}], {"a@x": []})["status"] == "ok"
    assert cc.check_keys([{}], {"ect-pipeline@x": [{"name": "k"}]})["status"] == "finding"
    ds = [{"datasetReference": {"datasetId": "raw"}, "location": "US", "labels": dict.fromkeys(cc.DATASET_LABELS, "x")},
          {"datasetReference": {"datasetId": "marts"}, "location": "US", "labels": {}, "defaultTableExpirationMs": "86400000"}]
    assert [x["status"] for x in cc.check_datasets(ds)] == ["ok", "finding"]
    assert cc.check_log_bucket({"retentionDays": 30})["status"] == "finding"
    wf = {"a.yml": "steps:\n  - uses: actions/checkout@v4\n  - uses: ./local\n  - uses: x/y@" + "a" * 40 + "\n"}
    assert cc.unpinned_actions(wf) == ["a.yml: actions/checkout@v4"]
    r = cc.check_github([{"type": "pull_request"}], wf, None)
    assert [x["status"] for x in r] == ["ok", "finding", "not_checked"]
    assert cc.check_github(None, {}, True)[0]["status"] == "not_checked"
    assert [x["status"] for x in cc.check_github([], {}, True)][1:] == ["ok", "ok"]
