import os
from supabase import create_client

BUCKET_NAME = "reels-queue"


def get_supabase():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SECRET_KEY")

    if not url or not key:
        raise RuntimeError("Supabase credentials missing.")

    return create_client(url, key)


def delete_published_video(storage_path, reel):
    # Safety checks — never delete unpublished videos
    if reel.get("status") != "published":
        raise RuntimeError("Deletion blocked: Reel not published.")

    if not reel.get("instagram_media_id"):
        raise RuntimeError("Deletion blocked: Instagram confirmation missing.")

    if reel.get("deleted_from_storage", False):
        return True

    client = get_supabase()

    result = client.storage.from_(BUCKET_NAME).remove([storage_path])

    reel["deleted_from_storage"] = True

    print(f"Cloud video deleted: {storage_path}")

    return True
