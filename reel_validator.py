from pathlib import Path

def validate_reel(video_path):
    video = Path(video_path)

    if not video.exists():
        return False, "Video file not found"

    if video.suffix.lower() != ".mp4":
        return False, "Only MP4 videos are allowed"

    if video.stat().st_size == 0:
        return False, "Video file is empty"

    return True, "Video passed validation"
