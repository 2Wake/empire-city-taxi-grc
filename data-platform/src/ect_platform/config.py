"""Fixed settings for the simulation. Changing any value here changes generated history."""
from datetime import date, timedelta
from pathlib import Path

# Bump when a code change alters generated output, so raw rows can be traced to the code that made them.
GENERATOR_VERSION = "0.6.0"

# Master seed. Every random choice derives from (SEED, stream name, date), so the
# same date always produces the same data no matter when or how often it is run.
SEED = "ect-2026"

# First simulated day. The batch for this day holds the starting population.
EPOCH = date(2026, 1, 1)

# Real trips come from the public NYC TLC 2022 yellow-taxi data (the newest full year
# in BigQuery's public dataset). Each simulated day maps to the 2022 day with the same
# weekday, cycling every 52 weeks, so weekday/weekend patterns stay realistic.
# The public 2022 table stops at 2022-11-30, so December dates replay the trips from
# 5 weeks earlier (same weekday, late Oct–Nov).
TLC_CYCLE_START = date(2022, 1, 3)   # a Monday
TLC_LAST_DAY = date(2022, 11, 30)    # last day present in the public 2022 table
_SIM_CYCLE_START = date(2025, 12, 29)  # the Monday on or before EPOCH


def tlc_date_for(day: date) -> date:
    """The 2022 TLC date whose trips are replayed on a simulated day."""
    src = TLC_CYCLE_START + timedelta(days=(day - _SIM_CYCLE_START).days % 364)
    return src - timedelta(weeks=5) if src > TLC_LAST_DAY else src


# Google Cloud
GCP_PROJECT = "empire-city-taxi"
RAW_DATASET = "raw"
LOCATION = "US"
TLC_SAMPLE_TABLE = f"{GCP_PROJECT}.{RAW_DATASET}.tlc_yellow_trips_sample"
# Hard cap on bytes any query from this package may bill. Reads of the TLC sample are tiny.
MAX_BYTES_BILLED = 1 * 1024**3  # 1 GiB

# Local folders (git-ignored)
ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = ROOT / "output"
TLC_CACHE_DIR = ROOT / ".cache" / "tlc"
# Named employees (leaders, stewards, staff) and the access policy matrix (shared with dbt)
ROSTER_PATH = Path(__file__).resolve().parent / "data" / "org_roster.csv"
ACCESS_POLICY_PATH = ROOT / "dbt" / "seeds" / "governance" / "access_policy.csv"
# POL-13 statement 16: records listed here (scope "record") are never written into a batch again, so a
# rebuild of `raw` can't bring back data that was disposed of.
DISPOSAL_LOG_PATH = ROOT / "dbt" / "seeds" / "governance" / "disposal_log.csv"

# Daily lifecycle rates (average events per day, Poisson)
RATES = {
    "corporate_hires": 0.08,
    "corporate_terminations": 0.06,
    "driver_hires": 0.45,
    "driver_terminations": 0.35,
    "driver_suspensions": 0.04,
    "rider_signups": 6.0,
    "rider_closures": 0.5,
    "rider_profile_updates": 2.0,
    "extra_cards": 0.8,
    "card_removals": 0.4,
    "new_campaigns": 0.08,
    "corporate_transfers": 0.03,
    "security_investigations": 0.05,
    "analyst_raw_requests": 0.01,
}

# Share of card-paid trips booked through the ECT app (the rest are street hails with no rider).
APP_BOOKED_SHARE = 0.7
SURVEY_SHARE = 0.06

# Planted data-quality defects: probability per new record. Carried over from Project 1,
# so the existing data-quality rules still apply. In 0.4.0 the four defects on full SSNs, card
# and bank numbers were redefined on the last-4 values that replaced them (same rates and the
# same random draws, so the same records carry them). Every planted defect is written to the
# answer key table gov_planted_defects.
DEFECT_RATES = {
    "driver_ssn_last4_short": 0.04,
    "driver_tlc_license_missing": 0.03,
    "driver_payout_last4_masked": 0.03,
    "driver_background_status_case": 0.15,
    "rider_email_missing": 0.03,
    "rider_email_invalid": 0.02,
    "rider_email_duplicate": 0.015,
    "card_last4_missing": 0.03,
    "survey_orphan_trip": 0.02,
    "survey_rating_out_of_range": 0.02,
    "survey_comment_contains_pii": 0.03,
    "employee_ssn_last4_masked": 0.03,
    "employee_salary_negative": 0.02,
    "employee_email_duplicate": 0.02,
    "ledger_account_missing": 0.02,
    "campaign_end_before_start": 0.05,
    # access control (per grant, termination, transfer or expiry)
    "access_self_approved": 0.02,
    "access_missing_approval": 0.02,
    "access_wrong_approver": 0.02,
    "access_not_revoked_on_termination": 0.2,
    "access_retained_after_transfer": 0.3,
    "access_expired_still_active": 0.2,
    # from HR_DEFECTS_START (0.6.0): a new driver made active while the background check is still
    # pending, and HR never records the result (POL-14 statement 4; check HR-01)
    "driver_activated_before_check": 0.1,
}
HR_DEFECTS_START = date(2026, 12, 1)


# Roster corrections that take effect on a given day, so history already loaded stays as it was.
# Before that day the person's HR record has a blank role_code (as originally generated); on that
# day HR corrects it and a new version of the record is emitted. Key: roster key.
ROSTER_CORRECTIONS = {
    "arjun.mehta": date(2026, 11, 24),   # VP Engineering was missing role_code vp-engineering
}


# Policy acknowledgments (from 0.5.0; POL-01 statement 6, STD-01 section 11). SIMULATED.
# Staff were asked on 2026-11-28 (blog 950312) to acknowledge all 15 policies and DOC-04 with one
# comment by 2026-12-09; drivers do it in the ECT Driver app. Each person acknowledges every document
# at once, on a day drawn from the weights below. Simulated acknowledgments start on ACK_START, the first
# day not yet loaded when this was built, so history already in `raw` stays as it was.
# The document list is fixed here (not read from the Policy Register seed) so a later register edit
# can't change generated history. A new major version would need a new campaign (not modelled yet).
ACK_START = date(2026, 11, 28)
ACK_DOCS = [("POL-01", "1.2"), ("POL-02", "2.0"), ("POL-03", "2.0"), ("POL-04", "2.0"), ("POL-05", "1.1"),
            ("POL-06", "1.0"), ("POL-07", "1.1"), ("POL-08", "1.2"), ("POL-09", "1.0"), ("POL-10", "1.0"),
            ("POL-11", "1.0"), ("POL-12", "1.0"), ("POL-13", "1.0"), ("POL-14", "1.0"), ("POL-15", "1.0"),
            ("DOC-04", "1.0")]
# Weight of acknowledging on day k after the request, for the 2026-12-09 deadline:
#   staff: BUSINESS day k, counted from the first business day on or after the request (2026-11-28 is a
#          Saturday, so k = 0 is Monday 11-30 and k = 7 is the deadline). k = 8 to 16 is late: k = 12 is
#          5 business days overdue, when council item 4.5 option B escalates to the VP People.
#   drivers: CALENDAR day k (the app asks when they go online, any day): k = 11 is the deadline,
#          12 to 25 is late.
# The rest (ACK_NEVER, 2%) never acknowledge, which feeds the last escalation step. Staff hired later
# count from their hire date (due 10 business days later, so the same weights are on time).
ACK_WEIGHTS = {
    "staff":   [22, 14, 10, 7, 6, 7, 10, 12,
                3, 1.5, 1, 0.8, 0.7, 1, 0.8, 0.6, 0.6],
    "drivers": [12, 14, 16, 10, 7, 6, 5, 5, 4, 3, 3, 3,
                2, 1.5, 1, 1, 0.8, 0.7, 0.6, 0.5, 0.5, 0.4, 0.3, 0.3, 0.2, 0.2],
}
ACK_NEVER = 2


# Security awareness training (from 0.6.0; POL-14 section 5.3, decision 3(c): a Confluence course with a
# short quiz). SIMULATED. The courses open on TRAINING_START. Staff employed then must finish by
# TRAINING_DEADLINE (GOV-110); anyone hired later, within 10 business days of starting. TRN-03 (role
# training) is for staff with access to `raw` or `staging` (sensitive-access roles), due before that access
# (POL-14 statement 9). Each completion is a passed quiz (score 80 to 100).
TRAINING_START = date(2026, 12, 1)
TRAINING_DEADLINE = date(2027, 2, 24)
TRAINING_COURSES = {"TRN-01": "1.0", "TRN-02": "1.0", "TRN-03": "1.0"}
# Campaign (current staff): weight of finishing in WEEK w after TRAINING_START (week 12 holds the
# deadline; weeks 3 and 4 are the holidays), then late weeks 13 to 17. The rest never finish.
TRAINING_WEEK_WEIGHTS = [16, 10, 6, 3, 3, 8, 8, 7, 6, 7, 7, 6, 3, 3, 2, 1.5, 1, 0.5]
# New hires and new sensitive access: weight of business day k after assignment (k <= 9 on time for hires).
TRAINING_NEW_WEIGHTS = [10, 12, 12, 12, 10, 10, 8, 6, 5, 5, 2, 1.5, 1.2, 1, 0.8, 0.6, 0.5, 0.4]
TRAINING_NEVER = 2
