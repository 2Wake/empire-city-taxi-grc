"""Day-by-day simulation of Empire City Taxi.

The simulation always replays from EPOCH, so the state on any date (who is employed,
which riders are active, ...) is fixed. Each day's batch holds only the records created
or changed that day, like an incremental extract from each source system. Nothing is
ever deleted: terminations, closures and removals arrive as changed rows.

Each part of the business (HR, riders, marketing, ...) draws from its own random stream
keyed by date, so adding a feature to one part doesn't shift the data of the others.
"""
import csv
from collections import defaultdict
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from zoneinfo import ZoneInfo

from . import fakes
from .config import (ACCESS_POLICY_PATH, ACK_DOCS, ACK_NEVER, ACK_START, ACK_WEIGHTS, APP_BOOKED_SHARE,
                     DEFECT_RATES as DR, EPOCH, HR_DEFECTS_START, RATES, TRAINING_COURSES, TRAINING_DEADLINE,
                     TRAINING_NEVER, TRAINING_NEW_WEIGHTS, TRAINING_START, TRAINING_WEEK_WEIGHTS,
                     ROSTER_CORRECTIONS, ROSTER_PATH, SURVEY_SHARE, tlc_date_for)
from .fakes import poisson, rng

NY = ZoneInfo("America/New_York")

# Departments (governance-org-structure.md) and how many generic employees each gets, relatively
DEPARTMENT_WEIGHTS = {
    "Customer Support": 4, "Engineering": 3, "Operations": 2, "Finance": 2, "Marketing": 2, "People": 2,
    "Security": 2, "Data & Analytics": 2, "Rider Experience": 2, "Driver Operations": 2,
    "Legal & Privacy": 1, "Data Governance": 1,
}
# The data domain each department's "own domain" access refers to
DEPARTMENT_DOMAIN = {
    "Rider Experience": "rider", "Customer Support": "rider", "Driver Operations": "driver",
    "Operations": "trips", "Engineering": "trips", "Finance": "finance", "People": "people",
    "Marketing": "marketing", "Security": "risk", "Legal & Privacy": "risk",
    "Data Governance": "governance", "Data & Analytics": "trips", "Executive": "governance",
}
DOMAIN_OWNER_ROLE = {
    "rider": "vp-rider-experience", "driver": "vp-driver-operations", "trips": "vp-operations",
    "finance": "cfo", "people": "vp-people", "marketing": "vp-marketing", "risk": "ciso",
    "governance": "data-governance-manager",
}
# Warehouse access role a generic (unnamed) employee gets on joining, and how often
DEFAULT_ACCESS = {
    "Data & Analytics": ("data_analyst", 1.0), "Data Governance": ("governance_admin", 1.0),
    "Finance": ("domain_analyst", 0.5), "Marketing": ("domain_analyst", 0.5),
    "Operations": ("domain_analyst", 0.5), "People": ("domain_analyst", 0.3),
    "Rider Experience": ("domain_analyst", 0.3), "Driver Operations": ("domain_analyst", 0.3),
    "Security": ("security_analyst", 0.3),
}


def _read_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


ROSTER = _read_csv(ROSTER_PATH)
POLICY = {(p["access_role"], p["dataset"]): p for p in _read_csv(ACCESS_POLICY_PATH)}
TITLES = ["Analyst", "Specialist", "Engineer", "Coordinator", "Manager", "Lead", "Director"]
RATINGS = ["exceeds", "meets", "meets", "meets", "below", "not_rated"]
CHANNELS = ["email", "paid_social", "search", "referral", "out_of_home", "push"]
CAMPAIGN_THEMES = ["Airport Express", "Late Night Safe Ride", "Commuter Saver", "Weekend Out",
                   "Welcome Back", "Refer a Friend", "Rainy Day", "Holiday Travel", "Business Rides"]
SEGMENTS = [
    ("New riders", "created_at < 30 days"), ("Lapsed", "no trip in 90 days"),
    ("Airport frequent", "3+ airport trips/mo"), ("Night owls", "trips after midnight"),
    ("High value", "top 10% spend"), ("Commuters", "weekday AM/PM peaks"),
    ("Weekend", "Sat/Sun only"), ("Promo responders", "redeemed a promo"),
    ("Business", "expense-tagged trips"), ("Tourists", "out-of-state cards"),
    ("Tippers", "avg tip > 20%"), ("At risk", "declining frequency"),
]
LEDGER_ACCOUNTS = ["revenue_rider_fares", "revenue_tips", "cogs_driver_payouts",
                   "opex_marketing", "opex_payroll", "opex_cloud"]
SURVEY_COMMENTS = ["Great driver, smooth ride.", "Clean car, on time.", "Driver took a long route.",
                   "Friendly and quick.", "Car smelled of smoke.", "Perfect, thank you!",
                   "A bit of a bumpy ride.", "Excellent service.", "", ""]


class Simulation:
    def __init__(self):
        self.employees: dict[str, dict] = {}
        self.drivers: dict[str, dict] = {}
        self.riders: dict[str, dict] = {}
        self.cards: dict[str, dict] = {}
        self.campaigns: dict[str, dict] = {}
        self.segments: dict[str, dict] = {}
        self.grants: dict[str, dict] = {}
        self.roster: dict[str, str] = {}          # roster key -> employee_id
        self.role_holders: dict[str, str] = {}    # role_code -> employee_id
        self.department_heads: dict[str, str] = {}
        # Employees carrying a planted "access left in place" defect. They are kept out of later random
        # terminations and transfers, so a routine event can't silently clean the defect up.
        self.protected: set[str] = set()
        self.seq = defaultdict(int)
        self.agenda = defaultdict(list)       # date -> [(action, id)] scheduled follow-ups
        self.rider_emails: list[str] = []
        self.employee_emails: list[str] = []
        self.ack_plan: dict[str, date | None] = {}   # employee_id -> day they acknowledge (None: never)
        self.training_plan: dict[tuple[str, str], date | None] = {}   # (employee_id, course) -> day done
        self.day: date | None = None
        self._out = None
        self._defects = None

    # ------------------------------------------------------------------ plumbing
    def _next_id(self, prefix: str, base: int) -> str:
        self.seq[prefix] += 1
        return f"{prefix}{base + self.seq[prefix]}"

    def _ts(self, r, day: date | None = None, lo: int = 6, hi: int = 22) -> str:
        """A random NYC-local timestamp on `day` (default: today), as ISO 8601 with offset."""
        moment = datetime.combine(day or self.day, time()) + timedelta(seconds=r.randint(lo * 3600, hi * 3600 - 1))
        return moment.replace(tzinfo=NY).isoformat()

    def _touch(self, table: str, key: str, rec: dict) -> None:
        """Record that `rec` was created or changed today (latest image wins)."""
        if self._out is not None:
            self._out[table][key] = {k: v for k, v in rec.items() if not k.startswith("_")}

    def _plant(self, r, defect: str) -> bool:
        return r.random() < DR[defect]

    def _log_defect(self, table: str, record_id: str, column: str, code: str) -> None:
        if self._defects is not None:
            self._defects.append({"table_name": table, "record_id": record_id,
                                  "column_name": column, "defect_code": code})

    @staticmethod
    def _active(records: dict, field: str, value: str = "active") -> list[str]:
        return [k for k, v in records.items() if v[field] == value]

    # ------------------------------------------------------------------ one day
    def step(self, day: date, emit: bool = False, tlc_rows: list[dict] | None = None):
        """Advance the simulation through `day`. If `emit`, return that day's batch."""
        self.day = day
        self._out = defaultdict(dict) if emit else None
        self._defects = [] if emit else None
        if day == EPOCH:
            self._initial_population()
        else:
            self._run_agenda()
            self._people(rng("people", day))
            self._access_events(rng("access", day))
            self._riders(rng("riders", day))
            self._marketing(rng("marketing", day))
            self._finance(rng("finance", day))
            if day >= ACK_START:
                self._acknowledgments()
            if day >= TRAINING_START:
                self._training()
        if not emit:
            return None
        if tlc_rows is not None:
            self._trips(tlc_rows)
        batch = {table: list(rows.values()) for table, rows in self._out.items()}
        stamp = f"{day:%Y%m%d}"
        batch["gov_planted_defects"] = [
            {"defect_id": f"DEF{stamp}{i:04d}", **d} for i, d in enumerate(self._defects, 1)]
        return batch

    # ------------------------------------------------------------------ policy acknowledgments
    def _ack_day(self, eid: str, start: date, driver: bool) -> date | None:
        """The day this person acknowledges, counted from `start` (fixed per person; see ACK_WEIGHTS)."""
        r = rng("acks", eid)
        weights = ACK_WEIGHTS["drivers" if driver else "staff"]
        k = r.choices(range(len(weights) + 1), weights=[*weights, ACK_NEVER])[0]
        if k == len(weights):
            return None
        if driver:
            return start + timedelta(days=k)
        day = start
        while day.weekday() >= 5:      # a request on a weekend counts from the next business day
            day += timedelta(days=1)
        while k:
            day += timedelta(days=1)
            if day.weekday() < 5:
                k -= 1
        return day

    def _acknowledgments(self) -> None:
        """Each active employee acknowledges every document in ACK_DOCS at once: staff by commenting on
        the announcement (blog 950312), drivers in the ECT Driver app. Staff hired later count from hire."""
        for eid, emp in self.employees.items():
            if emp["employment_status"] != "active":
                continue
            driver = emp["department"] == "Driver Operations"
            if eid not in self.ack_plan:
                self.ack_plan[eid] = self._ack_day(eid, max(ACK_START, date.fromisoformat(emp["hired_at"])), driver)
            if self.ack_plan[eid] != self.day:
                continue
            r = rng("acks", eid, self.day)
            at = self._ts(r, lo=5, hi=23) if driver else self._ts(r, lo=8, hi=19)
            channel, evidence = (("driver_app", "ECT Driver app acknowledgment screen") if driver
                                 else ("confluence_comment", "Comment on Confluence blog 950312"))
            for doc_id, version in ACK_DOCS:
                major = version.split(".")[0]
                self._touch("hris_policy_acknowledgments", f"{eid}|{doc_id}", {
                    "ack_id": f"ACK-{eid}-{doc_id}-{major}", "employee_id": eid, "doc_id": doc_id,
                    "doc_version": version, "acknowledged_at": at, "channel": channel, "evidence": evidence})

    # ------------------------------------------------------------------ security awareness training
    @staticmethod
    def _add_business_days(start: date, k: int) -> date:
        day = start
        while day.weekday() >= 5:
            day += timedelta(days=1)
        while k:
            day += timedelta(days=1)
            if day.weekday() < 5:
                k -= 1
        return day

    def _training_day(self, eid: str, course: str, assigned: date) -> date | None:
        r = rng("training", eid, course)
        if assigned <= TRAINING_START:     # the launch campaign: spread over weeks to TRAINING_DEADLINE
            w = r.choices(range(len(TRAINING_WEEK_WEIGHTS) + 1), weights=[*TRAINING_WEEK_WEIGHTS, TRAINING_NEVER])[0]
            if w == len(TRAINING_WEEK_WEIGHTS):
                return None
            day = self._add_business_days(TRAINING_START, 5 * w + r.randint(0, 4))
            return min(day, TRAINING_DEADLINE) if w <= 12 else day
        k = r.choices(range(len(TRAINING_NEW_WEIGHTS) + 1), weights=[*TRAINING_NEW_WEIGHTS, TRAINING_NEVER])[0]
        return None if k == len(TRAINING_NEW_WEIGHTS) else self._add_business_days(assigned, k)

    def _training(self) -> None:
        """Each active employee takes TRN-01 (staff) or TRN-02 (drivers); staff with an active `raw` or
        `staging` grant also take TRN-03. A completion is one passed quiz."""
        sensitive = {g["employee_id"] for g in self.grants.values()
                     if g["grant_status"] == "active" and g["dataset"] in ("raw", "staging")}
        for eid, emp in self.employees.items():
            if emp["employment_status"] != "active":
                continue
            driver = emp["department"] == "Driver Operations"
            courses = ["TRN-02"] if driver else ["TRN-01"] + (["TRN-03"] if eid in sensitive else [])
            for course in courses:
                key = (eid, course)
                if key not in self.training_plan:
                    assigned = max(TRAINING_START, date.fromisoformat(emp["hired_at"]), self.day)
                    self.training_plan[key] = self._training_day(eid, course, assigned)
                if self.training_plan[key] != self.day:
                    continue
                r = rng("training", eid, course, self.day)
                self._touch("hris_training_completions", f"{eid}|{course}", {
                    "completion_id": f"TRC-{eid}-{course}-{self.day:%Y%m%d}", "employee_id": eid,
                    "course_id": course, "course_version": TRAINING_COURSES[course],
                    "completed_at": self._ts(r, lo=5, hi=23) if driver else self._ts(r, lo=8, hi=19),
                    "score": r.randint(80, 100)})

    # ------------------------------------------------------------------ people (HR + fleet)
    def _new_employee(self, r, hired: date, driver: bool, named: dict | None = None) -> dict:
        eid = self._next_id("EMP", 10000)
        first, last = (named["first_name"], named["last_name"]) if named else fakes.person(r)
        email = f"{first}.{last}@empirecitytaxi.example".lower().replace(" ", "").replace("'", "")
        if email in self.employee_emails:
            email = email.replace("@", f"{self.seq['EMP']}@")
        defects = []
        if self.employee_emails and self._plant(r, "employee_email_duplicate"):
            email = r.choice(self.employee_emails)
            defects.append(("email", "employee_email_duplicate"))
        self.employee_emails.append(email)
        clean_ssn = fakes.last4(fakes.ssn(r))   # the full SSN stays with the payroll provider
        ssn_last4 = clean_ssn
        if self._plant(r, "employee_ssn_last4_masked"):
            ssn_last4 = f"XXX-XX-{clean_ssn}"    # masked display value exported instead of the digits
            defects.append(("ssn_last4", "employee_ssn_last4_masked"))
        if driver:
            department, title, pay_type, salary = "Driver Operations", "Driver", "commission", None
        else:
            if named:
                department, title = named["department"], named["title"]
            else:
                department = r.choices(list(DEPARTMENT_WEIGHTS), weights=list(DEPARTMENT_WEIGHTS.values()))[0]
                title = r.choice(TITLES)
            pay_type = "salaried"
            salary = r.randint(55, 210) * 1000 + r.randint(0, 999)
            if self._plant(r, "employee_salary_negative"):
                salary = -salary
                defects.append(("salary", "employee_salary_negative"))
        rec = {
            "employee_id": eid, "first_name": first, "last_name": last, "email": email, "ssn_last4": ssn_last4,
            "department": department, "title": title, "pay_type": pay_type, "salary": salary,
            "performance_rating": "not_rated" if hired >= self.day - timedelta(days=90) else r.choice(RATINGS),
            "manager_id": (self.roster.get(named["manager_key"]) if named
                           else self.department_heads.get(department)),
            "role_code": (named["role_code"] or None) if named else None,
            "hired_at": hired.isoformat(), "employment_status": "active", "terminated_at": None,
            "record_updated_at": self._ts(r), "_ssn_last4": clean_ssn,
            **self._screening(eid, hired, driver),
        }
        self.employees[eid] = rec
        self._touch("hris_employees", eid, rec)
        for column, code in defects:
            self._log_defect("hris_employees", eid, column, code)
        return rec

    @staticmethod
    def _screening(eid: str, hired: date, driver: bool) -> dict:
        """Pre-employment screening and confidentiality agreement (POL-14). Uses its own random
        stream keyed by employee ID, so adding it changed no other value. Drivers are screened
        through the fleet background check (fleet_drivers.background_check_status) instead."""
        if driver:
            return {"screening_status": None, "screening_date": None, "confidentiality_agreed_on": None}
        r = rng("hr-screening", eid)
        return {"screening_status": "clear",
                "screening_date": (hired - timedelta(days=r.randint(5, 30))).isoformat(),
                "confidentiality_agreed_on": hired.isoformat()}

    def _terminate_employee(self, r, eid: str, ts: str) -> None:
        emp = self.employees[eid]
        emp.update(employment_status="terminated", terminated_at=self.day.isoformat(), record_updated_at=ts)
        self._touch("hris_employees", eid, emp)
        self._revoke_all(r, eid, "termination", "access_not_revoked_on_termination")

    def _background_status(self, r, did: str, status: str) -> str:
        if self._plant(r, "driver_background_status_case"):
            self._log_defect("fleet_drivers", did, "background_check_status", "driver_background_status_case")
            return status.upper() if r.random() < 0.5 else status.capitalize()
        return status

    def _hire_driver(self, r, hired: date, onboarded: bool) -> None:
        emp = self._new_employee(r, hired, driver=True)
        did = self._next_id("DRV", 10000)
        ssn_last4 = emp["_ssn_last4"]
        if self._plant(r, "driver_ssn_last4_short"):
            ssn_last4 = ssn_last4[1:]              # leading digit lost in the export
            self._log_defect("fleet_drivers", did, "ssn_last4", "driver_ssn_last4_short")
        tlc = f"TLC{r.randint(100000, 999999)}"
        if self._plant(r, "driver_tlc_license_missing"):
            tlc = None
            self._log_defect("fleet_drivers", did, "tlc_license", "driver_tlc_license_missing")
        payout = fakes.last4(str(r.randint(10**8, 10**9 - 1)))   # the full account stays with the payout provider
        if self._plant(r, "driver_payout_last4_masked"):
            payout = f"*****{payout}"             # masked display value exported instead of the digits
            self._log_defect("fleet_drivers", did, "payout_account_last4", "driver_payout_last4_masked")
        ts = emp["record_updated_at"]
        if onboarded:
            background, status = self._background_status(r, did, "clear"), "active"
        else:
            background, status = "pending", "onboarding"
            result_day = self.day + timedelta(days=r.randint(3, 12))
            # Planted (0.6.0): activated before the check cleared, and the result is never recorded.
            # Own random stream, so no other value changes.
            early = (self.day >= HR_DEFECTS_START
                     and rng("driver-early-activation", did).random() < DR["driver_activated_before_check"])
            if early:
                status = "active"
                self._log_defect("fleet_drivers", did, "background_check_status", "driver_activated_before_check")
            else:
                self.agenda[result_day].append(("background_result", did))
        emp["manager_id"] = self.department_heads.get("Driver Operations")
        self.drivers[did] = {
            "driver_id": did, "employee_id": emp["employee_id"], "first_name": emp["first_name"],
            "last_name": emp["last_name"], "tlc_license": tlc, "ssn_last4": ssn_last4, "phone": fakes.phone(r),
            "home_address": fakes.nyc_address(r), "payout_account_last4": payout,
            "payout_account_token": fakes.payout_token(did),
            "background_check_status": background, "driver_status": status, "hired_at": hired.isoformat(),
            "status_changed_at": ts, "record_updated_at": ts,
        }
        self._touch("fleet_drivers", did, self.drivers[did])

    def _set_driver_status(self, r, did: str, status: str, **changes) -> str:
        drv = self.drivers[did]
        ts = self._ts(r)
        drv.update(driver_status=status, status_changed_at=ts, record_updated_at=ts, **changes)
        self._touch("fleet_drivers", did, drv)
        return ts

    def _correct_roster(self, key: str) -> None:
        """HR fixes a named person's role_code (see ROSTER_CORRECTIONS) and a new record version is emitted.
        Uses its own random stream so no other output for the day changes."""
        person = next(p for p in ROSTER if p["key"] == key)
        eid = self.roster[key]
        emp = self.employees[eid]
        emp["role_code"] = person["role_code"]
        emp["record_updated_at"] = self._ts(rng("roster_correction", self.day), lo=9, hi=17)
        self.role_holders[person["role_code"]] = eid
        self._touch("hris_employees", eid, emp)

    def _run_agenda(self) -> None:
        r = rng("agenda", self.day)
        for action, key in self.agenda.pop(self.day, []):
            if action == "roster_correction":
                self._correct_roster(key)
                continue
            if action == "expire_grant":
                self._expire_grant(r, key)
                continue
            if action == "default_access":
                emp = self.employees[key]
                if emp["employment_status"] == "active" and emp.get("_default_role"):
                    self._grant_role(r, key, emp["_default_role"], self._ts(r))
                continue
            did = key
            drv = self.drivers[did]
            if action == "background_result" and drv["driver_status"] == "onboarding":
                if r.random() < 0.9:
                    self._set_driver_status(r, did, "active",
                                            background_check_status=self._background_status(r, did, "clear"))
                else:
                    ts = self._set_driver_status(r, did, "inactive",
                                                 background_check_status=self._background_status(r, did, "flagged"))
                    self._terminate_employee(r, drv["employee_id"], ts)
            elif action == "reinstate" and drv["driver_status"] == "suspended":
                self._set_driver_status(r, did, "active")

    def _people(self, r) -> None:
        for _ in range(poisson(r, RATES["corporate_hires"])):
            emp = self._new_employee(r, self.day, driver=False)
            self._assign_default_access(r, emp, delay_days=r.randint(1, 5))
        for _ in range(poisson(r, RATES["corporate_terminations"])):
            generic = self._generic_corporate()
            if generic:
                self._terminate_employee(r, r.choice(generic), self._ts(r))
        for _ in range(poisson(r, RATES["corporate_transfers"])):
            generic = self._generic_corporate()
            if generic:
                self._transfer(r, r.choice(generic))
        for _ in range(poisson(r, RATES["driver_hires"])):
            self._hire_driver(r, self.day, onboarded=False)
        for _ in range(poisson(r, RATES["driver_terminations"])):
            active = self._active(self.drivers, "driver_status")
            if active:
                did = r.choice(active)
                ts = self._set_driver_status(r, did, "inactive")
                self._terminate_employee(r, self.drivers[did]["employee_id"], ts)
        for _ in range(poisson(r, RATES["driver_suspensions"])):
            active = self._active(self.drivers, "driver_status")
            if active:
                did = r.choice(active)
                self._set_driver_status(r, did, "suspended")
                self.agenda[self.day + timedelta(days=r.randint(7, 30))].append(("reinstate", did))
        if (self.day.month, self.day.day) == (3, 1):  # annual review: new ratings and merit raises
            for eid, emp in self.employees.items():
                if emp["employment_status"] == "active" and emp["pay_type"] == "salaried":
                    emp["performance_rating"] = r.choice(RATINGS)
                    emp["salary"] = round(emp["salary"] * (1 + r.choice([0, 0.02, 0.03, 0.04, 0.06])))
                    emp["record_updated_at"] = self._ts(r)
                    self._touch("hris_employees", eid, emp)

    # ------------------------------------------------------------------ warehouse access (IAM)
    def _generic_corporate(self) -> list[str]:
        named = set(self.roster.values())
        return [k for k, v in self.employees.items() if v["employment_status"] == "active"
                and v["pay_type"] == "salaried" and k not in named and k not in self.protected]

    def _assign_default_access(self, r, emp: dict, delay_days: int = 0) -> None:
        role, share = DEFAULT_ACCESS.get(emp["department"], (None, 0))
        emp["_default_role"] = role if role and r.random() < share else None
        if emp["_default_role"] and delay_days:
            self.agenda[self.day + timedelta(days=delay_days)].append(("default_access", emp["employee_id"]))

    def _expected_approver(self, role: str, dataset: str, scope: str, eid: str) -> str:
        policy = POLICY.get((role, dataset))
        approver_role = policy["approver_role"] if policy else "cdo"
        if approver_role == "domain-owner":
            approver_role = DOMAIN_OWNER_ROLE[scope]
        holder = self.role_holders[approver_role]
        if holder == eid:   # nobody approves their own access: escalate
            holder = self.role_holders["ceo" if approver_role == "cdo" else "cdo"]
        return holder

    def _grant_role(self, r, eid: str, role: str, ts: str) -> None:
        department = self.employees[eid]["department"]
        for (policy_role, dataset), policy in POLICY.items():
            if policy_role != role or policy["time_bound_days"]:
                continue
            scope = DEPARTMENT_DOMAIN[department] if policy["domain_scope"] == "own" else policy["domain_scope"]
            self._grant(r, eid, role, dataset, scope, ts)

    def _grant(self, r, eid: str, role: str, dataset: str, scope: str, ts: str, *, days: int | None = None,
               approver: str | None = None, plants: bool = True) -> str:
        gid = self._next_id("GRT", 100000)
        emp = self.employees[eid]
        expected = self._expected_approver(role, dataset, scope, eid)
        approved_by, ticket = approver or expected, f"REQ{gid[3:]}"
        code = None
        if plants:
            roll = r.random()
            if roll < DR["access_self_approved"]:
                approved_by, code = eid, "access_self_approved"
            elif roll < DR["access_self_approved"] + DR["access_missing_approval"]:
                approved_by, ticket, code = None, None, "access_missing_approval"
            elif roll < DR["access_self_approved"] + DR["access_missing_approval"] + DR["access_wrong_approver"]:
                others = sorted(h for h in set(self.role_holders.values()) if h not in (expected, eid))
                approved_by, code = r.choice(others), "access_wrong_approver"
        policy = POLICY.get((role, dataset))
        granted_day = date.fromisoformat(ts[:10])
        self.grants[gid] = {
            "grant_id": gid, "employee_id": eid, "access_role": role, "dataset": dataset, "domain_scope": scope,
            "privilege": policy["privilege"] if policy else "read", "granted_for_department": emp["department"],
            "request_ticket": ticket, "requested_by": emp.get("manager_id") or eid, "approved_by": approved_by,
            "granted_at": ts, "expires_at": (granted_day + timedelta(days=days)).isoformat() if days else None,
            "revoked_at": None, "revoke_reason": None, "grant_status": "active", "record_updated_at": ts,
        }
        self._touch("iam_access_grants", gid, self.grants[gid])
        if code:
            self._log_defect("iam_access_grants", gid, "approved_by", code)
        if days:
            self.agenda[granted_day + timedelta(days=days)].append(("expire_grant", gid))
        return gid

    def _end_grant(self, r, gid: str, status: str, reason: str) -> None:
        ts = self._ts(r)
        self.grants[gid].update(grant_status=status, revoked_at=ts, revoke_reason=reason, record_updated_at=ts)
        self._touch("iam_access_grants", gid, self.grants[gid])

    def _active_grants(self, eid: str) -> list[str]:
        return [g for g, v in self.grants.items() if v["employee_id"] == eid and v["grant_status"] == "active"]

    def _revoke_all(self, r, eid: str, reason: str, defect: str) -> None:
        grants = self._active_grants(eid)
        if not grants:
            return
        if self._plant(r, defect):   # access left in place: planted defect on every grant
            self.protected.add(eid)
            for gid in grants:
                self._log_defect("iam_access_grants", gid, "grant_status", defect)
            return
        for gid in grants:
            self._end_grant(r, gid, "revoked", reason)

    def _expire_grant(self, r, gid: str) -> None:
        if self.grants[gid]["grant_status"] != "active":
            return
        if self._plant(r, "access_expired_still_active"):
            self.protected.add(self.grants[gid]["employee_id"])
            self._log_defect("iam_access_grants", gid, "expires_at", "access_expired_still_active")
        else:
            self._end_grant(r, gid, "expired", "time limit reached")

    def _transfer(self, r, eid: str) -> None:
        emp = self.employees[eid]
        new = r.choices([d for d in DEPARTMENT_WEIGHTS if d != emp["department"]],
                        weights=[w for d, w in DEPARTMENT_WEIGHTS.items() if d != emp["department"]])[0]
        emp.update(department=new, title=r.choice(TITLES), manager_id=self.department_heads.get(new),
                   record_updated_at=self._ts(r))
        self._touch("hris_employees", eid, emp)
        self._revoke_all(r, eid, "transfer", "access_retained_after_transfer")
        self._assign_default_access(r, emp, delay_days=r.randint(1, 5))

    def _holders(self, role: str) -> list[str]:
        return sorted({v["employee_id"] for v in self.grants.values()
                       if v["access_role"] == role and v["grant_status"] == "active"
                       and self.employees[v["employee_id"]]["employment_status"] == "active"})

    def _access_events(self, r) -> None:
        # Security investigations: time-bound raw access (policy maximum 14 days)
        for _ in range(poisson(r, RATES["security_investigations"])):
            analysts = self._holders("security_analyst")
            if analysts:
                self._grant(r, r.choice(analysts), "security_analyst", "raw", "all", self._ts(r),
                            days=r.randint(5, 14))
        # Planted: an analyst asks for raw access and her manager approves it (not allowed by policy)
        for _ in range(poisson(r, RATES["analyst_raw_requests"])):
            analysts = [a for a in self._holders("data_analyst") if a != self.role_holders["data-analytics"]]
            if analysts:
                gid = self._grant(r, r.choice(analysts), "data_analyst", "raw", "all", self._ts(r),
                                  approver=self.role_holders["data-analytics"], plants=False)
                self.protected.add(self.grants[gid]["employee_id"])
                self._log_defect("iam_access_grants", gid, "dataset", "access_exceeds_policy")

    # ------------------------------------------------------------------ riders and cards
    def _new_rider(self, r, created_ts: str) -> str:
        rid = self._next_id("RDR", 100000)
        first, last = fakes.person(r)
        email = f"{first}.{last}{self.seq['RDR']}@example.com".lower().replace(" ", "").replace("'", "")
        roll = r.random()
        if roll < DR["rider_email_missing"]:
            email, code = None, "rider_email_missing"
        elif roll < DR["rider_email_missing"] + DR["rider_email_invalid"]:
            email, code = email.replace("@", "."), "rider_email_invalid"
        elif self.rider_emails and roll < sum(DR[k] for k in ("rider_email_missing", "rider_email_invalid",
                                                              "rider_email_duplicate")):
            email, code = r.choice(self.rider_emails), "rider_email_duplicate"
        else:
            code = None
        if email and "@" in email:
            self.rider_emails.append(email)
        self.riders[rid] = {
            "rider_id": rid, "first_name": first, "last_name": last, "email": email,
            "phone": fakes.phone(r), "home_address": fakes.nyc_address(r), "created_at": created_ts,
            "account_status": "active", "closed_at": None, "record_updated_at": self._ts(r),
        }
        self._touch("app_riders", rid, self.riders[rid])
        if code:
            self._log_defect("app_riders", rid, "email", code)
        return rid

    def _add_card(self, r, rid: str, added_ts: str | None = None) -> None:
        cid = self._next_id("CRD", 100000)
        last4 = fakes.last4(fakes.card_number(r))  # the processor keeps the card number; ECT gets last 4 + token
        if self._plant(r, "card_last4_missing"):
            last4 = None                               # processor response arrived without the last 4
            self._log_defect("payments_rider_cards", cid, "card_last4", "card_last4_missing")
        rider = self.riders[rid]
        holder = (f"{rider['first_name']} {rider['last_name']}" if r.random() < 0.9
                  else " ".join(fakes.person(r)))
        ts = added_ts or self._ts(r)
        self.cards[cid] = {
            "card_id": cid, "rider_id": rid, "card_token": fakes.card_token(cid), "card_last4": last4,
            "card_expiry": f"{r.randint(1, 12):02d}/{self.day.year % 100 + r.randint(1, 5)}",
            "cardholder_name": holder, "card_status": "active", "added_at": ts,
            "record_updated_at": self._ts(r),
        }
        self._touch("payments_rider_cards", cid, self.cards[cid])

    def _remove_card(self, r, cid: str) -> None:
        card = self.cards[cid]
        card.update(card_status="removed", record_updated_at=self._ts(r))
        self._touch("payments_rider_cards", cid, card)

    def _riders(self, r) -> None:
        for _ in range(poisson(r, RATES["rider_signups"])):
            rid = self._new_rider(r, self._ts(r, lo=0, hi=24))
            if r.random() < 0.85:
                self._add_card(r, rid)
        active = self._active(self.riders, "account_status")
        for _ in range(poisson(r, RATES["rider_closures"])):
            rid = r.choice(active)
            rider = self.riders[rid]
            ts = self._ts(r)
            rider.update(account_status="closed", closed_at=ts, record_updated_at=ts)
            self._touch("app_riders", rid, rider)
            for cid, card in self.cards.items():
                if card["rider_id"] == rid and card["card_status"] == "active":
                    self._remove_card(r, cid)
        active = self._active(self.riders, "account_status")
        for _ in range(poisson(r, RATES["rider_profile_updates"])):
            rider = self.riders[r.choice(active)]
            if r.random() < 0.5:
                rider["phone"] = fakes.phone(r)
            else:
                rider["home_address"] = fakes.nyc_address(r)
            rider["record_updated_at"] = self._ts(r)
            self._touch("app_riders", rider["rider_id"], rider)
        for _ in range(poisson(r, RATES["extra_cards"])):
            self._add_card(r, r.choice(active))
        active_cards = self._active(self.cards, "card_status")
        for _ in range(poisson(r, RATES["card_removals"])):
            self._remove_card(r, r.choice(active_cards))

    # ------------------------------------------------------------------ marketing and finance
    def _new_campaign(self, r, start: date) -> None:
        cid = self._next_id("CMP", 1000)
        end = start + timedelta(days=r.randint(7, 60))
        if self._plant(r, "campaign_end_before_start"):
            end = start - timedelta(days=r.randint(1, 10))
            self._log_defect("app_marketing_campaigns", cid, "end_date", "campaign_end_before_start")
        self.campaigns[cid] = {
            "campaign_id": cid, "name": f"{r.choice(CAMPAIGN_THEMES)} {start:%b %Y}",
            "channel": r.choice(CHANNELS), "start_date": start.isoformat(), "end_date": end.isoformat(),
            "budget": r.randint(20, 800) * 100, "target_segment_id": r.choice(list(self.segments)),
            "record_updated_at": self._ts(r),
        }
        self._touch("app_marketing_campaigns", cid, self.campaigns[cid])

    def _marketing(self, r) -> None:
        for _ in range(poisson(r, RATES["new_campaigns"])):
            self._new_campaign(r, self.day + timedelta(days=r.randint(3, 20)))
        if self.day.day == 1:
            for sid, seg in self.segments.items():
                seg["size_estimate"] = max(100, round(seg["size_estimate"] * r.uniform(0.92, 1.12)))
                seg["record_updated_at"] = self._ts(r)
                self._touch("app_rider_segments", sid, seg)

    def _post_ledger(self, r, year: int, month: int, recorded_ts: str) -> None:
        for i, account in enumerate(LEDGER_ACCOUNTS, 1):
            entry_id = f"JE{year}{month:02d}{i:02d}"
            amount = Decimal(r.randint(5_000_000, 90_000_000)) / 100
            if account.startswith(("cogs", "opex")):
                amount = -amount
            if self._plant(r, "ledger_account_missing"):
                account = None
                self._log_defect("payments_financial_ledger", entry_id, "account", "ledger_account_missing")
            self._touch("payments_financial_ledger", entry_id, {
                "entry_id": entry_id, "period": f"{year}-{month:02d}", "account": account,
                "amount": str(amount), "currency": "USD", "recorded_at": recorded_ts})

    def _finance(self, r) -> None:
        if self.day.day == 3:
            prior = self.day.replace(day=1) - timedelta(days=1)
            self._post_ledger(r, prior.year, prior.month, self._ts(r, lo=9, hi=18))

    # ------------------------------------------------------------------ starting population
    def _initial_population(self) -> None:
        r = rng("initial", EPOCH)
        for person in ROSTER:                       # named staff first: EMP10001 is the CEO
            if not person["manager_key"] or next(
                    p for p in ROSTER if p["key"] == person["manager_key"])["department"] != person["department"]:
                self.department_heads.setdefault(person["department"], None)
        for person in ROSTER:
            fix_day = ROSTER_CORRECTIONS.get(person["key"])
            as_hired = {**person, "role_code": ""} if fix_day else person   # role_code arrives on fix_day
            emp = self._new_employee(r, date.fromisoformat(person["hired_at"]), driver=False, named=as_hired)
            self.roster[person["key"]] = emp["employee_id"]
            if as_hired["role_code"]:
                self.role_holders[person["role_code"]] = emp["employee_id"]
            if fix_day:
                self.agenda[fix_day].append(("roster_correction", person["key"]))
            if person["department"] in self.department_heads and self.department_heads[person["department"]] is None:
                self.department_heads[person["department"]] = emp["employee_id"]
        for emp in list(self.employees.values()):   # managers are known only once everyone exists
            person = next(p for p in ROSTER if p["first_name"] == emp["first_name"] and p["last_name"] == emp["last_name"])
            emp["manager_id"] = self.roster.get(person["manager_key"])
            emp["_default_role"] = person["access_role"] if person["access_role"] != "business_user" else None
            self._touch("hris_employees", emp["employee_id"], emp)
        for _ in range(150):
            emp = self._new_employee(r, EPOCH - timedelta(days=r.randint(30, 2500)), driver=False)
            self._assign_default_access(r, emp)
        for _ in range(300):
            self._hire_driver(r, EPOCH - timedelta(days=r.randint(60, 2200)), onboarded=True)
        # Warehouse access for everyone who has a role, granted a few days after hire
        for eid, emp in list(self.employees.items()):
            if emp.get("_default_role"):
                hired = date.fromisoformat(emp["hired_at"])
                self._grant_role(r, eid, emp["_default_role"], self._ts(r, hired + timedelta(days=r.randint(1, 5))))
        # Planted: an analyst holds raw access, approved by her manager (policy allows analysts marts only)
        chloe = self.roster["chloe.bennett"]
        gid = self._grant(r, chloe, "data_analyst", "raw", "all", self._ts(r, EPOCH - timedelta(days=40)),
                          approver=self.roster["aisha.karim"], plants=False)
        self._log_defect("iam_access_grants", gid, "dataset", "access_exceeds_policy")
        for _ in range(2000):
            self._new_rider(r, self._ts(r, EPOCH - timedelta(days=r.randint(1, 1460)), lo=0, hi=24))
        rider_ids = list(self.riders)
        for _ in range(1800):
            rid = r.choice(rider_ids)
            self._add_card(r, rid, added_ts=max(self.riders[rid]["created_at"], self._ts(r, EPOCH - timedelta(days=r.randint(1, 900)))))
        for i, (name, definition) in enumerate(SEGMENTS, 1):
            sid = f"SEG{i:02d}"
            self.segments[sid] = {"segment_id": sid, "name": name, "definition": definition,
                                  "size_estimate": r.randint(500, 40000), "record_updated_at": self._ts(r)}
            self._touch("app_rider_segments", sid, self.segments[sid])
        for _ in range(40):
            self._new_campaign(r, EPOCH - timedelta(days=r.randint(0, 500)))
        for year in (2024, 2025):
            for month in range(1, 13 if year == 2024 else 12):  # Dec 2025 posts on 2026-01-03
                posted = date(year + (month == 12), month % 12 + 1, 3)
                self._post_ledger(r, year, month, self._ts(r, posted, lo=9, hi=18))

    # ------------------------------------------------------------------ trips (real TLC + synthetic people)
    def _trips(self, tlc_rows: list[dict]) -> None:
        r = rng("trips", self.day)
        shift = self.day - tlc_date_for(self.day)
        drivers = self._active(self.drivers, "driver_status")
        riders = self._active(self.riders, "account_status")
        stamp = f"{self.day:%Y%m%d}"
        survey_no = 0
        rows = sorted(tlc_rows, key=lambda t: (t["pickup_datetime"], t["tlc_sample_key"]))
        for i, t in enumerate(rows, 1):
            trip_id = f"TRP{stamp}{i:05d}"
            pickup = datetime.fromisoformat(t["pickup_datetime"]) + shift
            dropoff = datetime.fromisoformat(t["dropoff_datetime"]) + shift
            booked = t["payment_type"] == "1" and r.random() < APP_BOOKED_SHARE
            rider_id = r.choice(riders) if booked else None
            self._touch("app_trips", trip_id, {
                "trip_id": trip_id, "driver_id": r.choice(drivers), "rider_id": rider_id,
                "pickup_datetime": pickup.isoformat(sep=" "), "dropoff_datetime": dropoff.isoformat(sep=" "),
                "passenger_count": t["passenger_count"], "trip_distance": t["trip_distance"],
                "rate_code": t["rate_code"], "payment_type": t["payment_type"],
                "fare_amount": t["fare_amount"], "extra": t["extra"], "mta_tax": t["mta_tax"],
                "tip_amount": t["tip_amount"], "tolls_amount": t["tolls_amount"],
                "improvement_surcharge": t["imp_surcharge"], "airport_fee": t["airport_fee"],
                "total_amount": t["total_amount"], "pickup_location_id": t["pickup_location_id"],
                "dropoff_location_id": t["dropoff_location_id"], "tlc_source_key": t["tlc_sample_key"],
            })
            if rider_id and r.random() < SURVEY_SHARE:
                submitted = dropoff + timedelta(minutes=r.randint(2, 90))
                if submitted.date() != self.day:
                    continue
                survey_no += 1
                self._survey(r, f"SRV{stamp}{survey_no:04d}", trip_id, rider_id, submitted)

    def _survey(self, r, sid: str, trip_id: str, rider_id: str, submitted: datetime) -> None:
        rating = r.choices([1, 2, 3, 4, 5], weights=[4, 4, 10, 30, 52])[0]
        comment = r.choice(SURVEY_COMMENTS) or None
        if self._plant(r, "survey_orphan_trip"):
            trip_id = f"TRP{self.day:%Y%m%d}{r.randint(90000, 99999)}"
            self._log_defect("app_trip_surveys", sid, "trip_id", "survey_orphan_trip")
        if self._plant(r, "survey_rating_out_of_range"):
            rating = r.choice([0, 6, 9, -1])
            self._log_defect("app_trip_surveys", sid, "rating", "survey_rating_out_of_range")
        if self._plant(r, "survey_comment_contains_pii"):
            name = fakes.person(r)[0].lower()
            comment = f"Left my bag in the cab, call me at {fakes.phone(r)} or {name}@example.com"
            self._log_defect("app_trip_surveys", sid, "comment", "survey_comment_contains_pii")
        self._touch("app_trip_surveys", sid, {
            "survey_id": sid, "trip_id": trip_id, "rider_id": rider_id, "rating": rating,
            "comment": comment, "submitted_at": submitted.isoformat(sep=" ")})
