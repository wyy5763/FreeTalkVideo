from pathlib import Path
import subprocess
from .config import settings

class VideoError(RuntimeError):
    pass

def _run(args, cwd=None):
    try:
        p = subprocess.run(args, cwd=cwd, capture_output=True, text=True)
    except FileNotFoundError as exc:
        raise VideoError(f"找不到FFmpeg：{settings.ffmpeg_bin}") from exc
    if p.returncode != 0:
        raise VideoError(p.stderr[-5000:] or "FFmpeg执行失败")
    return p

def make_static_talking_video(avatar: Path, audio: Path, output: Path):
    args = [
        settings.ffmpeg_bin, "-y",
        "-loop", "1", "-i", str(avatar),
        "-i", str(audio),
        "-vf", "scale=1080:1920:force_original_aspect_ratio=decrease,"
               "pad=1080:1920:(ow-iw)/2:(oh-ih)/2",
        "-c:v", "libx264", "-preset", "veryfast", "-tune", "stillimage",
        "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
        "-shortest", str(output)
    ]
    _run(args)
    return output

def add_subtitles(video: Path, subtitle: Path, output: Path):
    subtitle_filter = subtitle.resolve().as_posix().replace(":", "\:")
    args = [
        settings.ffmpeg_bin, "-y", "-i", str(video),
        "-vf", f"subtitles='{subtitle_filter}'",
        "-c:a", "copy", str(output)
    ]
    _run(args)
    return output

def probe(path: Path) -> dict:
    args = [
        settings.ffmpeg_bin, "-v", "error", "-show_entries",
        "format=duration:stream=codec_name,width,height",
        "-of", "default=noprint_wrappers=1", str(path)
    ]
    try:
        p = subprocess.run(args, capture_output=True, text=True)
    except FileNotFoundError:
        return {}
    if p.returncode != 0:
        return {}
    result = {}
    for line in p.stdout.splitlines():
        if "=" in line:
            k, v = line.split("=", 1)
            result[k] = v
    return result
