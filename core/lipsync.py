from pathlib import Path
import subprocess
from .config import settings

class LipSyncError(RuntimeError):
    pass

def run_musetalk(avatar: Path, audio: Path, output: Path) -> Path:
    root = Path(settings.musetalk_root)
    if not root.exists():
        raise LipSyncError("MUSETALK_ROOT未配置或目录不存在")

    candidates = [
        root / "scripts" / "inference.py",
        root / "inference.py",
        root / "scripts" / "inference.sh",
    ]
    entry = next((p for p in candidates if p.exists()), None)
    if entry is None:
        raise LipSyncError("未找到MuseTalk推理入口，请按当前版本README适配CLI")

    if entry.suffix == ".sh":
        cmd = ["bash", str(entry), str(avatar), str(audio), str(output)]
    else:
        cmd = [
            settings.musetalk_python, str(entry),
            "--avatar", str(avatar),
            "--audio", str(audio),
            "--output", str(output),
        ]
    p = subprocess.run(cmd, cwd=root, capture_output=True, text=True)
    if p.returncode != 0:
        raise LipSyncError(p.stderr[-4000:] or "MuseTalk执行失败")
    if not output.exists():
        raise LipSyncError("MuseTalk执行完成但没有找到输出视频")
    return output
