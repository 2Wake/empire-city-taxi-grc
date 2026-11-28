"""Read-only check of the cloud project and repository settings against the policies (GOV-159; F15).

    uv run ect-config-check            # check, print, and write config-checks/<date>.md
    uv run ect-config-check --check    # also exit 1 if any check is a finding

Only reads; never changes a setting. Each setting that doesn't match is a FINDING to record and route, not
fix here (POL-07: changes go through the owner). Runs monthly from GitHub Actions (config-check.yml) and on
demand. Needs read access to IAM policy, service accounts, datasets and log buckets: Security Reviewer,
Logs Viewer and BigQuery Metadata Viewer on the account it runs as (`ect-monitor`, setup part L). Locally it uses your own gcloud sign-in.

Privacy: the repository is public, so people show as `maintainer` or a hash, never an email.
"""
import argparse
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime

from .config import GCP_PROJECT, ROOT
from .security_review import display, load_identities
from .sim import NY

CHECKS_DIR = ROOT / "config-checks"
REPO = "2Wake/empire-city-taxi-grc"

# Project-level role bindings the policies allow (POL-02 Appendix A; setup docs). Anything else is a finding.
EXPECTED_PROJECT_BINDINGS = {
    "roles/owner": {"maintainer"},
    "roles/bigquery.jobUser": {"ect-pipeline", "ect-role-analyst", "ect-role-security", "ect-role-steward", "ect-watchdog"},
    "roles/bigquery.metadataViewer": {"ect-catalog", "ect-watchdog", "ect-monitor"},
    "roles/dataplex.catalogEditor": {"ect-catalog"},
    "roles/logging.privateLogViewer": {"ect-monitor"},
    "roles/bigquerydatatransfer.serviceAgent": {"google-service-agent (bigquerydatatransfer)"},
    "roles/iam.securityReviewer": {"ect-monitor"},
    "roles/logging.viewer": {"ect-monitor"},
}
DATA_ACCESS_SERVICES = {"iam.googleapis.com", "sts.googleapis.com"}   # BigQuery's are always on
DATASET_LABELS = {"layer", "classification", "data_custodian", "environment", "managed_by"}
LOG_RETENTION_DAYS = 400   # POL-09 statement 12 (owner setting 2026-11-25; final decision GOV-94)


def _session():
    import google.auth
    from google.auth.transport.requests import AuthorizedSession
    creds, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform.read-only"])
    return AuthorizedSession(creds)


def _github(path: str):
    req = urllib.request.Request(f"https://api.github.com/{path}", headers={"Accept": "application/vnd.github+json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


def result(check: str, policy: str, ok: bool | None, detail: str) -> dict:
    return {"check": check, "policy": policy, "status": "ok" if ok else ("finding" if ok is False else "not_checked"),
            "detail": detail}


def check_iam(policy: dict, ids: dict) -> list[dict]:
    out, unexpected = [], []
    for b in policy.get("bindings", []):
        members = {display(m.split(":", 1)[-1], ids) for m in b["members"]}
        extra = members - EXPECTED_PROJECT_BINDINGS.get(b["role"], set())
        unexpected += [f"{b['role']} → {m}" for m in sorted(extra)]
    out.append(result("CFG-01 Project roles match the access matrix", "POL-02 Appendix A", not unexpected,
                      "; ".join(unexpected) or "every project role binding is expected"))
    basic = [f"{b['role']} → {display(m.split(':', 1)[-1], ids)}" for b in policy.get("bindings", [])
             if b["role"] in ("roles/owner", "roles/editor", "roles/viewer")
             for m in b["members"] if display(m.split(":", 1)[-1], ids) != "maintainer"]
    out.append(result("CFG-02 Basic roles (owner, editor, viewer) held by the maintainer only", "POL-02 st. 3",
                      not basic, "; ".join(basic) or "only the maintainer"))
    audit = {a["service"]: {c["logType"] for c in a.get("auditLogConfigs", [])} for a in policy.get("auditConfigs", [])}
    missing = [s for s in DATA_ACCESS_SERVICES if not {"DATA_READ", "DATA_WRITE", "ADMIN_READ"} <= audit.get(s, set())]
    out.append(result("CFG-03 Data Access audit logs on for IAM and STS", "POL-09 st. 2", not missing,
                      ("missing: " + ", ".join(sorted(missing))) if missing else "on for " + ", ".join(sorted(DATA_ACCESS_SERVICES))))
    return out


def check_keys(accounts: list[dict], keys_by_account: dict) -> dict:
    with_keys = [a.split("@")[0] for a, keys in keys_by_account.items() if keys]
    return result("CFG-04 No user-managed service account keys", "POL-02 st. 14", not with_keys,
                  ", ".join(with_keys) or f"none on {len(accounts)} service accounts")


def check_datasets(datasets: list[dict]) -> list[dict]:
    out = []
    for d in datasets:
        name = d["datasetReference"]["datasetId"]
        missing = DATASET_LABELS - set(d.get("labels", {}))
        expiry = d.get("defaultTableExpirationMs")
        problems = ([f"missing labels {sorted(missing)}"] if missing else []) + \
                   ([f"default table expiry {int(expiry) // 86400000} days"] if expiry else []) + \
                   ([f"location {d.get('location')}"] if d.get("location") != "US" else [])
        out.append(result(f"CFG-05 Dataset `{name}`: labels, no default expiry, US", "POL-03, POL-13", not problems,
                          "; ".join(problems) or "all five labels; no default expiry; US"))
    return out


def check_log_bucket(bucket: dict) -> dict:
    days = bucket.get("retentionDays", 30)
    locked = bucket.get("locked", False)
    return result("CFG-06 `_Default` log bucket keeps logs 400 days", "POL-09 st. 12", days >= LOG_RETENTION_DAYS,
                  f"{days} days, {'locked' if locked else 'not locked'}")


def unpinned_actions(workflows: dict[str, str]) -> list[str]:
    """Third-party `uses:` lines not pinned to a full 40-character commit (POL-10 st. 1)."""
    out = []
    for name, text in sorted(workflows.items()):
        for m in re.finditer(r"uses:\s*([^\s#]+)", text):
            ref = m.group(1)
            if ref.startswith("./") or re.search(r"@[0-9a-f]{40}$", ref):
                continue
            out.append(f"{name}: {ref}")
    return out


def check_github(rules: list | None, workflows: dict[str, str], alerts: bool | None) -> list[dict]:
    pr_rule = rules is not None and any(r.get("type") == "pull_request" for r in rules)
    loose = unpinned_actions(workflows)
    return [
        result("CFG-07 `main` requires a pull request (ruleset)", "POL-07 5.3", pr_rule if rules is not None else None,
               "pull request rule active on main" if pr_rule else
               ("no pull-request rule on main (GOV-77)" if rules is not None else "couldn't read the rules")),
        result("CFG-08 Actions pinned to a full commit", "POL-10 st. 1", not loose,
               f"{len(loose)} not pinned: " + "; ".join(sorted({x.split(': ')[1] for x in loose})) if loose
               else "every action pinned to a commit"),
        result("CFG-09 Dependabot vulnerability alerts on", "POL-10 st. 1", alerts,
               {True: "on", False: "off",
                None: "not checked: needs a token with admin read (check Settings → Code security)"}[alerts]),
    ]


def dependabot_alerts_on() -> bool | None:
    """True/False from the API when a token allows it (local `gh auth token`); None otherwise."""
    token = os.environ.get("GH_ADMIN_TOKEN")
    if not token:
        try:
            token = subprocess.run(["gh", "auth", "token"], capture_output=True, text=True, timeout=10).stdout.strip()
        except (OSError, subprocess.SubprocessError):
            token = ""
    if not token:
        return None
    req = urllib.request.Request(f"https://api.github.com/repos/{REPO}/vulnerability-alerts",
                                 headers={"Accept": "application/vnd.github+json", "Authorization": f"Bearer {token}"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status == 204
    except urllib.error.HTTPError as e:
        return False if e.code == 404 else None
    except OSError:
        return None


def run() -> list[dict]:
    ids = load_identities(os.environ.get("ECT_MAINTAINER_PRINCIPAL"))
    results = []
    s = _session()
    try:
        pol = s.post(f"https://cloudresourcemanager.googleapis.com/v1/projects/{GCP_PROJECT}:getIamPolicy",
                     json={"options": {"requestedPolicyVersion": 3}}, timeout=30)
        pol.raise_for_status()
        results += check_iam(pol.json(), ids)
    except Exception as e:  # noqa: BLE001
        results.append(result("CFG-01 to 03 Project IAM and audit settings", "POL-02, POL-09", None, f"couldn't read: {type(e).__name__}"))
    try:
        accts = s.get(f"https://iam.googleapis.com/v1/projects/{GCP_PROJECT}/serviceAccounts", timeout=30)
        accts.raise_for_status()
        accounts = accts.json().get("accounts", [])
        keys = {}
        for a in accounts:
            k = s.get(f"https://iam.googleapis.com/v1/{a['name']}/keys?keyTypes=USER_MANAGED", timeout=30)
            k.raise_for_status()
            keys[a["email"]] = k.json().get("keys", [])
        results.append(check_keys(accounts, keys))
    except Exception as e:  # noqa: BLE001
        results.append(result("CFG-04 No user-managed service account keys", "POL-02 st. 14", None, f"couldn't read: {type(e).__name__}"))
    try:
        ds = []
        for name in ("raw", "staging", "marts"):
            r = s.get(f"https://bigquery.googleapis.com/bigquery/v2/projects/{GCP_PROJECT}/datasets/{name}", timeout=30)
            r.raise_for_status()
            ds.append(r.json())
        results += check_datasets(ds)
    except Exception as e:  # noqa: BLE001
        results.append(result("CFG-05 Datasets", "POL-03, POL-13", None, f"couldn't read: {type(e).__name__}"))
    try:
        b = s.get(f"https://logging.googleapis.com/v2/projects/{GCP_PROJECT}/locations/global/buckets/_Default", timeout=30)
        b.raise_for_status()
        results.append(check_log_bucket(b.json()))
    except Exception as e:  # noqa: BLE001
        results.append(result("CFG-06 `_Default` log bucket keeps logs 400 days", "POL-09 st. 12", None, f"couldn't read: {type(e).__name__}"))
    try:
        rules = _github(f"repos/{REPO}/rules/branches/main")
    except Exception:  # noqa: BLE001
        rules = None
    wf_dir = ROOT.parent / ".github" / "workflows"
    workflows = {p.name: p.read_text() for p in wf_dir.glob("*.yml")}
    results += check_github(rules, workflows, dependabot_alerts_on())
    return results


def write(results: list[dict]) -> str:
    now = datetime.now(NY)
    findings = [r for r in results if r["status"] == "finding"]
    lines = [f"# Configuration check — {now:%Y-%m-%d}", "",
             f"- Run at: {now:%Y-%m-%d %H:%M %Z}", "- Read-only (`ect-config-check`, GOV-159). Findings are recorded, not fixed.",
             f"- Result: {len(results) - len(findings)} ok, {len(findings)} findings, "
             f"{sum(r['status'] == 'not_checked' for r in results)} not checked", "",
             "| Check | Policy | Status | Detail |", "|---|---|---|---|"]
    lines += [f"| {r['check']} | {r['policy']} | {r['status']} | {r['detail']} |" for r in results]
    CHECKS_DIR.mkdir(exist_ok=True)
    path = CHECKS_DIR / f"{now:%Y-%m-%d}.md"
    path.write_text("\n".join(lines) + "\n")
    return str(path)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true", help="exit 1 if any check is a finding")
    args = ap.parse_args(argv)
    results = run()
    for r in results:
        print(f"{r['status'].upper():12} {r['check']}: {r['detail']}")
    print(f"Wrote {write(results)}")
    return 1 if args.check and any(r["status"] == "finding" for r in results) else 0


if __name__ == "__main__":
    sys.exit(main())
