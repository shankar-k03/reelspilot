import json
import logging
from datetime import datetime, timezone, date
from pathlib import Path

from reel_validator import validate_reel

# -------------------------
# PATHS
# -------------------------
QUEUE_FILE = Path("data/queue.json")
VIDEO_FOLDER = Path("videos")
LOG_FOLDER = Path("logs")
LOG_FILE = LOG_FOLDER / "reelspilot.log"

MAX_ATTEMPTS = 3

# -------------------------
# LOGGING
# -------------------------
LOG_FOLDER.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler()
    ]
)

# -------------------------
# QUEUE FUNCTIONS
# -------------------------
def load_queue():
    if not QUEUE_FILE.exists():
        raise FileNotFoundError("Queue file not found")

    with open(QUEUE_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def save_queue(queue):
    with open(QUEUE_FILE, "w", encoding="utf-8") as file:
        json.dump(queue, file, indent=4)


def find_due_reel(queue):
    today = date.today().isoformat()

    for reel in queue.get("reels", []):
        if reel.get("status") == "published":
            continue

        if reel.get("status") == "failed":
            continue

        if reel.get("status") != "pending":
            continue

        if reel.get("scheduled_date", "") > today:
            continue

        if reel.get("attempts", 0) >= MAX_ATTEMPTS:
            reel["status"] = "failed"
            reel["error"] = "Maximum retry limit reached"
            continue

        return reel

    return None


# -------------------------
# REEL PROCESSING
# -------------------------
def process_reel(reel):
    reel_id = reel.get("id", "unknown")

    logging.info("Processing Reel: %s", reel_id)

    reel["attempts"] = reel.get("attempts", 0) + 1
    reel["last_attempt"] = datetime.now(timezone.utc).isoformat()

    try:
        video_path = VIDEO_FOLDER / reel["video"]

        valid, message = validate_reel(video_path)

        logging.info("Validation: %s", message)

        if not valid:
            raise ValueError(message)

        # Instagram publishing is not connected yet.
        logging.info("Video validation successful.")
        logging.info("Publishing integration is pending.")

        reel["error"] = None
        return True

    except Exception as error:
        reel["error"] = str(error)

        logging.error("Reel failed: %s", error)

        if reel["attempts"] >= MAX_ATTEMPTS:
            reel["status"] = "failed"
            logging.error("Maximum attempts reached. Reel permanently failed.")
        else:
            reel["status"] = "pending"
            logging.warning(
                "Reel will be retried. Attempt %s/%s",
                reel["attempts"],
                MAX_ATTEMPTS
            )

        return False


# -------------------------
# MAIN AUTOMATION
# -------------------------
def main():
    logging.info("========== ReelsPilot Started ==========")

    try:
        queue = load_queue()

        reel = find_due_reel(queue)

        if reel is None:
            save_queue(queue)
            logging.info("No Reel is due for processing.")
            return

        success = process_reel(reel)

        if success:
            logging.info("Reel passed validation.")
            logging.info("Waiting for Instagram publishing integration.")
        else:
            logging.warning("Reel processing failed.")

        save_queue(queue)

    except Exception:
        logging.exception("Automation encountered an unexpected error.")

    logging.info("========== ReelsPilot Finished ==========")


if __name__ == "__main__":
    main()
