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
                 speed: float, use_musetalk: bool, add_srt: bool):
    if not topic.strip():
        raise PipelineError("请输入主题或口播稿")

    avatar_path = Path(avatar) if avatar else None
    if not avatar_path or not avatar_path.exists():
        raise PipelineError("请上传头像图片")

    job = settings.output_dir / uuid.uuid4().hex
    job.mkdir(parents=True, exist_ok=True)

    if len(topic.strip()) > 120:
        script = topic.strip()
    else:
        script = generate_script(topic.strip(), style, seconds)

    (job / "script.txt").write_text(script, encoding="utf-8")
    audio = synthesize(script, job / "speech.wav", speed=speed)

    if use_musetalk:
        try:
            video = run_musetalk(avatar_path, audio, job / "talking.mp4")
        except LipSyncError as exc:
            raise PipelineError(
                f"MuseTalk模式失败：{exc}\n\n"
                "取消“使用MuseTalk”可以先验证LLM→TTS→FFmpeg全流程。"
            ) from exc
    else:
        video = make_static_talking_video(avatar_path, audio, job / "base.mp4")

    if add_srt:
        srt = write_basic_srt(script, audio, job / "subtitle.srt")
        final = add_subtitles(video, srt, job / "final.mp4")
    else:
        final = video

    return str(final), script, str(audio)
