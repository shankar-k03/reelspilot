import json
from datetime import datetime, timezone
from pathlib import Path

REPORT_FILE = Path("logs/run_report.json")


def save_report(reel_id, status, attempts=0, error=None):
    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)

    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "reel_id": reel_id,
        "status": status,
        "attempts": attempts,
        "error": error
    }

    if REPORT_FILE.exists():
        with open(REPORT_FILE, "r", encoding="utf-8") as file:
            reports = json.load(file)
    else:
        reports = []

    reports.append(entry)

    with open(REPORT_FILE, "w", encoding="utf-8") as file:
        json.dump(reports, file, indent=4)

    return entry


if __name__ == "__main__":
    print("ReelsPilot Report module ready.")
