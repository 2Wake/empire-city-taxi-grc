"""Guarantees the platform depends on. Run: uv run pytest"""
import random
import re
from datetime import date, timedelta

from ect_platform import fakes
from ect_platform.config import EPOCH, TLC_CYCLE_START, TLC_LAST_DAY, tlc_date_for
from ect_platform.generate import generate
from ect_platform.registry import TABLES, columns
from ect_platform.sim import Simulation


def _fake_tlc_rows(day, n=200):
    r = random.Random(day.toordinal())
    rows = []
    for i in range(n):
        pickup = f"{day} {r.randint(0, 22):02d}:{r.randint(0, 59):02d}:00"
        rows.append({
            "tlc_sample_key": str(i), "vendor_id": "1", "pickup_datetime": pickup,
            "dropoff_datetime": pickup[:-5] + "59:59", "passenger_count": "1", "trip_distance": "2.1",
            "rate_code": "1", "payment_type": r.choice(["1", "1", "2"]), "fare_amount": "12.5", "extra": "0.5",
            "mta_tax": "0.5", "tip_amount": "2", "tolls_amount": "0", "imp_surcharge": "0.3",
            "airport_fee": None, "total_amount": "15.8", "pickup_location_id": "161", "dropoff_location_id": "237",
        })
    return rows


def _run(days, with_trips=False):
    sim, out, day = Simulation(), {}, EPOCH
    while day <= max(days):
        rows = _fake_tlc_rows(tlc_date_for(day)) if with_trips and day in days else None
        out[day] = sim.step(day, emit=day in days, tlc_rows=rows)
        day += timedelta(days=1)
    return {d: out[d] for d in days}


def test_same_date_same_data_regardless_of_what_else_is_generated():
    target = date(2026, 6, 15)
    alone = _run([target], with_trips=True)[target]
    with_others = _run([date(2026, 2, 1), target, date(2026, 7, 1)], with_trips=True)[target]
    assert alone == with_others


def test_written_files_are_byte_identical(tmp_path):
    a = generate([date(2026, 3, 1)], with_trips=False, out_dir=tmp_path / "a")
    b = generate([date(2026, 3, 1)], with_trips=False, out_dir=tmp_path / "b")
    assert a == b  # manifests include SHA-256 of every file


def test_tlc_mapping_keeps_weekday_and_stays_in_available_data():
    for offset in range(0, 800):
        day = EPOCH + timedelta(days=offset)
        src = tlc_date_for(day)
        assert src.weekday() == day.weekday()
        assert TLC_CYCLE_START <= src <= TLC_LAST_DAY


def test_ids_are_prefixed():
    batch = _run([date(2026, 5, 5)], with_trips=True)[date(2026, 5, 5)]
    patterns = {"app_trips": ("trip_id", r"TRP\d{13}"), "fleet_drivers": ("driver_id", r"DRV\d{5}"),
                "hris_employees": ("employee_id", r"EMP\d{5}"), "app_riders": ("rider_id", r"RDR\d{6}")}
    for table, (col, pattern) in patterns.items():
        for row in batch.get(table, []):
            assert re.fullmatch(pattern, row[col]), (table, row[col])


def test_trips_use_only_active_drivers():
    sim, day = Simulation(), EPOCH
    target = date(2026, 4, 10)
    while day < target:
        sim.step(day)
        day += timedelta(days=1)
    batch = sim.step(target, emit=True, tlc_rows=_fake_tlc_rows(tlc_date_for(target)))
    for trip in batch["app_trips"]:
        assert sim.drivers[trip["driver_id"]]["driver_status"] == "active"


def test_every_batch_column_is_in_the_schema():
    batch = _run([EPOCH], with_trips=True)[EPOCH]
    for table, rows in batch.items():
        names = {c for c, _ in columns(table)}
        for row in rows:
            assert set(row) <= names, (table, set(row) - names)


def test_every_table_has_required_labels():
    required = {"domain", "layer", "data_owner", "data_steward", "classification", "source_system", "data_origin"}
    for table, spec in TABLES.items():
        assert required <= set(spec["labels"]), table


def test_card_numbers_pass_luhn():
    r = random.Random(1)
    for _ in range(100):
        digits = [int(c) for c in fakes.card_number(r).replace(" ", "")]
        total = sum(d if i % 2 == 0 else (d * 2 - 9 if d * 2 > 9 else d * 2)
                    for i, d in enumerate(reversed(digits)))
        assert total % 10 == 0


def test_answer_key_never_stores_values():
    batch = _run([EPOCH])[EPOCH]
    for row in batch["gov_planted_defects"]:
        assert set(row) == {"defect_id", "table_name", "record_id", "column_name", "defect_code"}


def _simulate_through(target):
    sim, day, planted = Simulation(), EPOCH, set()
    while day <= target:
        batch = sim.step(day, emit=True)
        planted |= {(d["record_id"], d["defect_code"]) for d in batch["gov_planted_defects"]}
        day += timedelta(days=1)
    return sim, planted


def test_named_roster_has_stable_ids_and_managers():
    sim, _ = _simulate_through(EPOCH)
    assert sim.roster["marcus.delgado"] == "EMP10001"
    assert sim.employees[sim.roster["jordan.ellis"]]["manager_id"] == sim.roster["renee.okonkwo"]
    assert sim.role_holders["ciso"] == sim.roster["victor.hale"]


def test_unplanted_grants_follow_the_access_policy():
    from ect_platform.sim import POLICY
    sim, planted = _simulate_through(date(2026, 6, 30))
    flagged = {gid for gid, _ in planted}
    for gid, g in sim.grants.items():
        if gid in flagged:
            continue
        assert (g["access_role"], g["dataset"]) in POLICY, g
        assert g["approved_by"] and g["approved_by"] != g["employee_id"], g


def test_business_users_and_drivers_have_no_warehouse_access():
    sim, _ = _simulate_through(EPOCH)
    support = sim.roster["monique.harris"]
    with_access = {g["employee_id"] for g in sim.grants.values()}
    assert support not in with_access
    assert not any(sim.employees[e]["title"] == "Driver" for e in with_access)


def test_roster_correction_arrives_on_its_day_and_leaves_history_unchanged():
    fix_day = date(2026, 11, 24)
    out = _run([EPOCH, fix_day - timedelta(days=1), fix_day])
    arjun = lambda batch: [e for e in batch.get("hris_employees", []) if e["last_name"] == "Mehta"]
    assert arjun(out[EPOCH])[0]["role_code"] is None                 # as originally loaded
    assert arjun(out[fix_day - timedelta(days=1)]) == []              # no change emitted before the fix
    assert arjun(out[fix_day])[0]["role_code"] == "vp-engineering"   # HR correction on fix_day


def _luhn_ok(digits: str) -> bool:
    total = sum(d if i % 2 == 0 else (d * 2 - 9 if d * 2 > 9 else d * 2)
                for i, d in enumerate(int(c) for c in reversed(digits)))
    return total % 10 == 0


def test_no_full_card_ssn_or_bank_numbers_leave_the_generator():
    """POL-04 / POL-11 (generator 0.4.0): only last-4 values and provider tokens are output."""
    out = _run([EPOCH, date(2026, 3, 2), date(2026, 9, 14)], with_trips=True)
    for batch in out.values():
        for table, rows in batch.items():
            for row in rows:
                for col, value in row.items():
                    if not isinstance(value, str):
                        continue
                    if col.endswith("_id"):   # numeric IDs (e.g. trip_id) can pass Luhn by chance
                        continue
                    for run in re.findall(r"\d[\d -]{11,22}\d", value):
                        digits = re.sub(r"\D", "", run)
                        assert not (13 <= len(digits) <= 19 and _luhn_ok(digits)), (table, col)
                    assert not re.search(r"\b\d{3}-\d{2}-\d{4}\b", value), (table, col)
                    if col.startswith(("ssn", "payout_account_last4", "card_last4")):
                        assert len(re.sub(r"\D", "", value)) <= 4, (table, col)
    assert not any("card_number" in columns(t) or "ssn" in dict(columns(t)) or "payout_bank_account" in dict(columns(t))
                   for t in TABLES)


def test_tokens_are_stable_and_not_derived_from_the_number():
    assert fakes.card_token("CRD100001") == fakes.card_token("CRD100001")
    assert fakes.card_token("CRD100001") != fakes.card_token("CRD100002")
    batch = _run([EPOCH])[EPOCH]
    cards = batch["payments_rider_cards"]
    assert all(c["card_token"] == fakes.card_token(c["card_id"]) for c in cards)
    assert all(re.fullmatch(r"tok_[A-Za-z]{24}", c["card_token"]) for c in cards)


def test_corporate_staff_have_screening_and_confidentiality_records():
    batch = _run([EPOCH])[EPOCH]
    staff = [e for e in batch["hris_employees"] if e["department"] != "Driver Operations" or e["title"] != "Driver"]
    assert staff and all(e["screening_status"] == "clear" and e["screening_date"] < e["hired_at"]
                         and e["confidentiality_agreed_on"] == e["hired_at"] for e in staff)


# ---- policy acknowledgments (0.5.0) ----

def test_acknowledgments_start_on_ack_start_and_cover_every_document():
    from ect_platform.config import ACK_DOCS, ACK_START
    days = [ACK_START - timedelta(days=1), ACK_START, ACK_START + timedelta(days=2)]
    out = _run(days)
    assert not out[days[0]].get("hris_policy_acknowledgments")   # history before ACK_START unchanged
    rows = out[days[1]]["hris_policy_acknowledgments"] + out[days[2]]["hris_policy_acknowledgments"]
    assert rows
    by_person = {}
    for r in rows:
        by_person.setdefault(r["employee_id"], set()).add(r["doc_id"])
    assert all(docs == {d for d, _ in ACK_DOCS} for docs in by_person.values())   # one action covers all
    # 2026-11-28 is a Saturday: only drivers (app) acknowledge; staff start Monday
    assert {r["channel"] for r in out[days[1]]["hris_policy_acknowledgments"]} == {"driver_app"}
    assert _run([ACK_START])[ACK_START]["hris_policy_acknowledgments"] == out[days[1]]["hris_policy_acknowledgments"]


# ---- training and early activation (0.6.0) ----

def test_training_starts_on_launch_with_the_right_course_per_person():
    from ect_platform.config import TRAINING_START
    days = [TRAINING_START - timedelta(days=1), TRAINING_START, TRAINING_START + timedelta(days=1)]
    sim, out, day = Simulation(), {}, EPOCH
    while day <= max(days):
        b = sim.step(day, emit=day in days)
        if b:
            out[day] = b
        day += timedelta(days=1)
    assert not out[days[0]].get("hris_training_completions")
    rows = out[days[1]]["hris_training_completions"] + out[days[2]]["hris_training_completions"]
    assert rows and all(80 <= r["score"] <= 100 for r in rows)
    for r in rows:
        driver = sim.employees[r["employee_id"]]["department"] == "Driver Operations"
        assert (r["course_id"] == "TRN-02") == driver


def test_early_activation_is_planted_only_from_hr_defects_start():
    from ect_platform.config import HR_DEFECTS_START
    sim, day, planted = Simulation(), EPOCH, []
    while day <= HR_DEFECTS_START + timedelta(days=120):
        b = sim.step(day, emit=day >= HR_DEFECTS_START - timedelta(days=30))
        if b:
            planted += [(day, d["record_id"]) for d in b["gov_planted_defects"]
                        if d["defect_code"] == "driver_activated_before_check"]
        day += timedelta(days=1)
    assert planted and all(d >= HR_DEFECTS_START for d, _ in planted)
    for _, did in planted:   # stays active with the check pending: the result is never recorded
        assert sim.drivers[did]["background_check_status"] == "pending"


def test_disposed_records_are_never_written_again(tmp_path):
    from ect_platform.generate import disposed_records, write_batch
    log = tmp_path / "disposal_log.csv"
    log.write_text("disposal_id,scope,table_name,record_id\nDSP-1,record,app_riders,RDR10001\n"
                   "DSP-2,column,hris_employees,\n")
    disposed = disposed_records(log)
    assert disposed == {("app_riders", "RDR10001")}
    batch = {"app_riders": [{"rider_id": "RDR10001"}, {"rider_id": "RDR10002"}]}
    manifest = write_batch(EPOCH, batch, tmp_path, with_trips=False, disposed=disposed)
    assert manifest["tables"]["app_riders"]["rows"] == 1
    assert "RDR10001" not in (tmp_path / EPOCH.isoformat() / "app_riders.jsonl").read_text()
    assert disposed_records() == set()   # the real log has no record-level entries yet


def test_build_tools_manifest_is_current():
    from ect_platform import manifest
    assert manifest.main(["--check"]) == 0, "run: uv run ect-manifest"
