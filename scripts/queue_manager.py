import logging
from pathlib import Path

from reel_validator import validate_reel
from cloud_uploader import upload_video
from run_report import save_report

import json
from datetime import date

QUEUE_FILE = Path("data/queue.json")
VIDEO_FOLDER = Path("videos")
MAX_ATTEMPTS = 3

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")


def load_queue():
    with open(QUEUE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_queue(queue):
    with open(QUEUE_FILE, "w", encoding="utf-8") as f:
        json.dump(queue, f, indent=4)


def find_due_reel(queue):
    today = date.today().isoformat()

    for reel in queue.get("reels", []):
        if reel.get("status") != "pending":
            continue
        if reel.get("scheduled_date", "") > today:
            continue
        if reel.get("attempts", 0) >= MAX_ATTEMPTS:
            reel["status"] = "failed"
            reel["error"] = "Maximum attempts reached"
            continue
        return reel

    return None


def process_reel(queue, reel):
    reel["attempts"] = reel.get("attempts", 0) + 1
    reel["last_attempt"] = date.today().isoformat()

    try:
        video_path = VIDEO_FOLDER / reel["video"]

        valid, message = validate_reel(video_path)
        if not valid:
            raise ValueError(message)

        uploaded = upload_video(video_path, reel["id"])

        reel["storage_path"] = uploaded["storage_path"]
        reel["public_url"] = uploaded["public_url"]
        reel["status"] = "uploaded"
        reel["error"] = None

        save_queue(queue)
        save_report(reel["id"], "uploaded", reel["attempts"])

        logging.info("Reel %s uploaded to Supabase.", reel["id"])
        return True

    except Exception as error:
        reel["error"] = str(error)

        if reel["attempts"] >= MAX_ATTEMPTS:
            reel["status"] = "failed"
        else:
            reel["status"] = "pending"

        save_queue(queue)
        save_report(reel["id"], reel["status"], reel["attempts"], str(error))

        logging.exception("Reel processing failed.")
        return False


def main():
    logging.info("ReelsPilot started.")

    queue = load_queue()
    reel = find_due_reel(queue)

    if reel is None:
        save_queue(queue)
        logging.info("No Reel due.")
        return

    process_reel(queue, reel)

    logging.info("ReelsPilot finished.")


if __name__ == "__main__":
    main()
