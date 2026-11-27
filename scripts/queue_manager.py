from reel_validator import validate_reel
import json
from datetime import date
from pathlib import Path

QUEUE_FILE = Path("data/queue.json")


def load_queue():
    with open(QUEUE_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def find_next_reel(queue):
    today = date.today().isoformat()

    for reel in queue.get("reels", []):
        if reel.get("status") != "pending":
            continue

        if reel.get("scheduled_date", "") > today:
            continue

        return reel

    return None


def main():
    queue = load_queue()
    reel = find_next_reel(queue)

    print("🤖 ReelsPilot Queue Manager")
    print("==========================")

    if reel is None:
        print("No Reel is due for publishing.")
        return

    print("Reel found!")
    print("ID:", reel["id"])
    print("Video:", reel["video"])
    print("Caption:", reel["caption"])
    print("Scheduled:", reel["scheduled_date"])
    print("Status:", reel["status"])
    print()
    print("Queue check complete.")
    print("Publishing is not enabled yet.")


if __name__ == "__main__":
    main()
