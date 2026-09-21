from pathlib import Path
import uuid
from .config import settings
from .llm import generate_script
from .tts import synthesize
from .subtitles import write_basic_srt
from .video import make_static_talking_video, add_subtitles
from .lipsync import run_musetalk, LipSyncError

class PipelineError(RuntimeError):
    pass

def create_video(topic: str, avatar: str, style: str, seconds: int,
                 speed: float, use_musetalk: bool, add_srt: bool,
                 voice: str = "", reference_audio: str = ""):
    if not topic.strip():
        raise PipelineError("请输入主题或口播稿")
    avatar_path = Path(avatar) if avatar else None
    if not avatar_path or not avatar_path.exists():
        raise PipelineError("请上传头像图片")
    if use_musetalk and not settings.musetalk_enabled:
        raise PipelineError("当前是 CPU-only 模式，MuseTalk 已关闭。请取消“使用 MuseTalk 1.5”，先生成静态口播视频。")

    job = settings.output_dir / uuid.uuid4().hex
    job.mkdir(parents=True, exist_ok=True)
    script = topic.strip() if len(topic.strip()) > 120 else generate_script(topic.strip(), style, seconds)
    (job / "script.txt").write_text(script, encoding="utf-8")
    audio = synthesize(script, job / "speech.wav", voice=voice.strip() or None, speed=speed)

    if use_musetalk:
        try:
            video = run_musetalk(avatar_path, audio, job / "talking.mp4")
        except LipSyncError as exc:
            raise PipelineError(f"MuseTalk模式失败：{exc}") from exc
    else:
        video = make_static_talking_video(avatar_path, audio, job / "base.mp4")

    if add_srt:
        srt = write_basic_srt(script, audio, job / "subtitle.srt")
        final = add_subtitles(video, srt, job / "final.mp4")
    else:
        final = video
    return str(final), script, str(audio)
