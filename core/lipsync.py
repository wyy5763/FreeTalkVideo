from pathlib import Path
import shutil
import subprocess
import yaml
from .config import settings

class LipSyncError(RuntimeError):
    pass

def _required_path(value: str, label: str) -> Path:
    path = Path(value)
    if not value or not path.exists():
        raise LipSyncError(f"{label}不存在：{value or '<未配置>'}")
    return path

def run_musetalk(avatar: Path, audio: Path, output: Path) -> Path:
    root = _required_path(settings.musetalk_root, "MUSETALK_ROOT")
    audio = _required_path(str(audio), "音频")
    avatar = _required_path(str(avatar), "头像")

    version = settings.musetalk_version.lower()
    if version not in {"v1", "v15"}:
        raise LipSyncError("MUSETALK_VERSION只能是v1或v15")

    unet_path = settings.musetalk_unet_path or (
        str(root / "models" / ("musetalkV15" if version == "v15" else "musetalk")
             / ("unet.pth" if version == "v15" else "pytorch_model.bin"))
    )
    unet_config = settings.musetalk_unet_config or (
        str(root / "models" / ("musetalkV15" if version == "v15" else "musetalk") / "musetalk.json")
    )
    whisper_dir = settings.musetalk_whisper_dir or str(root / "models" / "whisper")

    for path, label in [
        (unet_path, "MuseTalk UNet权重"),
        (unet_config, "MuseTalk UNet配置"),
        (whisper_dir, "MuseTalk Whisper目录"),
    ]:
        if not Path(path).exists():
            raise LipSyncError(f"{label}不存在：{path}")

    work = output.parent / "musetalk"
    work.mkdir(parents=True, exist_ok=True)
    config_path = work / "task.yaml"
    result_dir = work / "results"
    result_dir.mkdir(parents=True, exist_ok=True)

    # MuseTalk 1.5 官方 inference.py 可以直接接收 image/video。
    # 这里使用图片作为单帧 avatar，避免用户额外准备一段静态视频。
    task = {
        "job": {
            "video_path": str(avatar.resolve()),
            "audio_path": str(audio.resolve()),
            "result_name": output.name,
        }
    }
    config_path.write_text(yaml.safe_dump(task, allow_unicode=True, sort_keys=False), encoding="utf-8")

    cmd = [
        settings.musetalk_python,
        "-m", "scripts.inference",
        "--inference_config", str(config_path),
        "--result_dir", str(result_dir),
        "--unet_model_path", str(Path(unet_path)),
        "--unet_config", str(Path(unet_config)),
        "--version", version,
        "--whisper_dir", str(Path(whisper_dir)),
        "--gpu_id", str(settings.musetalk_gpu_id),
        "--batch_size", str(settings.musetalk_batch_size),
    ]
    if settings.musetalk_float16:
        cmd.append("--use_float16")
    if settings.musetalk_ffmpeg_path:
        cmd += ["--ffmpeg_path", settings.musetalk_ffmpeg_path]

    try:
        p = subprocess.run(cmd, cwd=root, capture_output=True, text=True)
    except FileNotFoundError as exc:
        raise LipSyncError(f"找不到MuseTalk Python：{settings.musetalk_python}") from exc

    log = (p.stdout or "") + "\n" + (p.stderr or "")
    if p.returncode != 0:
        raise LipSyncError(log[-8000:] or "MuseTalk执行失败")

    candidates = [
        result_dir / version / output.name,
        result_dir / "v15" / output.name,
        result_dir / "v1" / output.name,
    ]
    found = next((p for p in candidates if p.exists()), None)
    if found is None:
        matches = list(result_dir.rglob("*.mp4"))
        found = matches[-1] if matches else None
    if found is None:
        raise LipSyncError("MuseTalk执行完成，但没有找到输出MP4。\n" + log[-4000:])

    if found.resolve() != output.resolve():
        shutil.copy2(found, output)
    return output
