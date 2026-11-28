"""Generate daily batches.

    uv run ect-generate                       # yesterday (New York time)
    uv run ect-generate --date 2026-11-23
    uv run ect-generate --start 2026-01-01 --end 2026-11-23
    uv run ect-generate --backfill            # EPOCH through yesterday
    add --no-trips to skip the real TLC trips (works offline, no Google sign-in needed)

Writes output/<date>/<table>.jsonl plus manifest.json (row counts and SHA-256 hashes).
"""
import argparse
import csv
import hashlib
import json
import shutil
from datetime import date, datetime, timedelta

from . import tlc
from .config import DISPOSAL_LOG_PATH, EPOCH, GENERATOR_VERSION, OUTPUT_DIR, tlc_date_for
from .registry import TABLES, columns
from .sim import NY, Simulation


def yesterday() -> date:
    return datetime.now(NY).date() - timedelta(days=1)


def generate(days: list[date], with_trips: bool = True, out_dir=OUTPUT_DIR) -> dict[date, dict]:
    wanted = set(days)
    if with_trips:
        tlc.ensure_cached({tlc_date_for(d) for d in wanted})
    sim = Simulation()
    disposed = disposed_records()
    results, day = {}, EPOCH
    while day <= max(wanted):
        if day in wanted:
            rows = tlc.read_day(tlc_date_for(day)) if with_trips else None
            batch = sim.step(day, emit=True, tlc_rows=rows)
            results[day] = write_batch(day, batch, out_dir, with_trips, disposed)
        else:
            sim.step(day)
        day += timedelta(days=1)
    return results


def disposed_records(path=DISPOSAL_LOG_PATH) -> set[tuple[str, str]]:
    """(table, record id) pairs disposed of under POL-13 statement 16. Column- and table-level entries
    (such as the 0.4.0 rebuild) are recorded in the log but have nothing to filter here."""
    if not path.exists():
        return set()
    with open(path, newline="", encoding="utf-8") as f:
        return {(row["table_name"], row["record_id"]) for row in csv.DictReader(f)
                if row["scope"] == "record" and row["record_id"]}


def write_batch(day: date, batch: dict, out_dir, with_trips: bool, disposed: set | None = None) -> dict:
    folder = out_dir / day.isoformat()
    shutil.rmtree(folder, ignore_errors=True)
    folder.mkdir(parents=True)
    manifest = {"batch_date": day.isoformat(), "generator_version": GENERATOR_VERSION,
                "includes_trips": with_trips, "tables": {}}
    for table in TABLES:
        rows = batch.get(table) or []
        if not rows:
            continue
        names = [c for c, _ in columns(table)]
        key = names[0]   # each table's first column is its record ID
        rows = [row for row in rows if (table, str(row.get(key))) not in (disposed or set())]
        if not rows:
            continue
        path = folder / f"{table}.jsonl"
        with open(path, "w") as f:
            for row in rows:
                row = {**row, "_batch_date": day.isoformat(), "_generator_version": GENERATOR_VERSION}
                f.write(json.dumps({c: row.get(c) for c in names}, ensure_ascii=False) + "\n")
        manifest["tables"][table] = {"rows": len(rows),
                                     "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
    (folder / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest


def parse_args(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--date", type=date.fromisoformat)
    p.add_argument("--start", type=date.fromisoformat)
    p.add_argument("--end", type=date.fromisoformat)
    p.add_argument("--backfill", action="store_true", help="every day from EPOCH through yesterday")
    p.add_argument("--no-trips", action="store_true", help="skip TLC trips and surveys (offline)")
    args = p.parse_args(argv)
    if args.backfill:
        start, end = EPOCH, yesterday()
    elif args.start or args.end:
        if not (args.start and args.end):
            p.error("--start and --end go together")
        start, end = args.start, args.end
    else:
        start = end = args.date or yesterday()
    if start < EPOCH or end < start:
        p.error(f"dates must be on or after {EPOCH} and start <= end")
    return [start + timedelta(days=i) for i in range((end - start).days + 1)], not args.no_trips


def main(argv=None):
    days, with_trips = parse_args(argv)
    print(f"Generating {len(days)} day(s): {days[0]} .. {days[-1]} (generator {GENERATOR_VERSION})")
    results = generate(days, with_trips)
    for day, manifest in results.items():
        counts = ", ".join(f"{t}={m['rows']}" for t, m in manifest["tables"].items())
        print(f"  {day}: {counts}")
    print(f"Done. Batches in {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
