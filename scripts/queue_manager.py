import json
import logging
from datetime import date
from pathlib import Path

from reel_validator import validate_reel

# Paths
QUEUE_FILE = Path("data/queue.json")
VIDEO_FOLDER = Path("videos")
LOG_FOLDER = Path("logs")
LOG_FILE = LOG_FOLDER / "reelspilot.log"

# Create log folder
LOG_FOLDER.mkdir(exist_ok=True)

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler()
    ]
)


def load_queue():
    if not QUEUE_FILE.exists():
        raise FileNotFoundError("Queue file not found.")

    with open(QUEUE_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def save_queue(queue):
    with open(QUEUE_FILE, "w", encoding="utf-8") as file:
        json.dump(queue, file, indent=4)


def find_due_reel(queue):
    today = date.today().isoformat()

    for reel in queue.get("reels", []):
        if reel.get("status") != "pending":
            continue

        if reel.get("scheduled_date", "") <= today:
            return reel

    return None


def process_reel(reel):
    video_path = VIDEO_FOLDER / reel["video"]

    valid, message = validate_reel(video_path)

    logging.info("Reel ID: %s", reel["id"])
    logging.info("Validation: %s", message)

    if not valid:
        reel["status"] = "failed"
        reel["error"] = message
        return False

    logging.info("Video validation successful.")
    logging.info("Reel is ready for publishing.")

    # Publishing will be connected through Instagram API later.
    return True


def main():
    logging.info("========== ReelsPilot Started ==========")

    try:
        queue = load_queue()
        reel = find_due_reel(queue)

        if reel is None:
            logging.info("No Reel is due today.")
            return

        if process_reel(reel):
            logging.info("Reel passed all checks.")
            logging.info("Publishing integration is pending.")
        else:
            logging.error("Reel failed validation.")

        save_queue(queue)

    except Exception as error:
        logging.exception("Automation error: %s", error)

    logging.info("========== ReelsPilot Finished ==========")


if __name__ == "__main__":
    main()
