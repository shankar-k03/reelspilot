import os
import mimetypes
from pathlib import Path

from supabase import create_client


BUCKET_NAME = "reels-queue"


def get_supabase():
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SECRET_KEY")

    if not url or not key:
        raise RuntimeError("Supabase credentials are missing.")

    return create_client(url, key)


def upload_video(video_path, reel_id):
    video = Path(video_path)

    if not video.exists():
        raise FileNotFoundError(f"Video not found: {video}")

    if video.suffix.lower() != ".mp4":
        raise ValueError("Only MP4 videos are supported.")

    client = get_supabase()

    storage_path = f"{reel_id}/{video.name}"
    content_type = mimetypes.guess_type(video.name)[0] or "video/mp4"

    with open(video, "rb") as file:
        client.storage.from_(BUCKET_NAME).upload(
            path=storage_path,
            file=file,
            file_options={
                "content-type": content_type,
                "upsert": "false"
            }
        )

    public_url = (
        client.storage.from_(BUCKET_NAME)
        .get_public_url(storage_path)
    )

    return {
        "storage_path": storage_path,
        "public_url": public_url
    }


if __name__ == "__main__":
    print("ReelsPilot Cloud Uploader is ready.")
