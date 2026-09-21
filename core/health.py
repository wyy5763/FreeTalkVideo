import shutil
from pathlib import Path
import requests
from .config import settings

def _ok(name, detail):
    return f"✅ {name}: {detail}"

def _bad(name, detail):
    return f"❌ {name}: {detail}"

def run_health_check() -> str:
    rows = ["FreeTalkVideo 系统检查", "=" * 32]
    ffmpeg = shutil.which(settings.ffmpeg_bin)
    rows.append(_ok("4. FFmpeg", ffmpeg) if ffmpeg else _bad("4. FFmpeg", f"找不到 {settings.ffmpeg_bin}"))

    try:
        r = requests.get(
            settings.llm_base_url.rstrip("/") + "/models",
            headers={"Authorization": f"Bearer {settings.llm_api_key}"},
            timeout=8,
        )
        rows.append(_ok("1. Qwen/LLM", f"{settings.llm_base_url} 可访问，模型={settings.llm_model}") if r.ok
                    else _bad("1. Qwen/LLM", f"HTTP {r.status_code}"))
    except Exception as exc:
        rows.append(_bad("1. Qwen/LLM", str(exc)))

    if settings.tts_mode == "native":
        root = Path(settings.cosyvoice_root)
        model = Path(settings.cosyvoice_model_dir)
        prompt = Path(settings.cosyvoice_prompt_wav)
        ok = root.exists() and model.exists() and prompt.exists()
        rows.append(_ok("2. CosyVoice3 native", f"root={root}, model={model}, prompt={prompt}") if ok
                    else _bad("2. CosyVoice3 native", f"root={root}, model={model}, prompt={prompt}"))
    else:
        try:
            r = requests.get(
                settings.tts_base_url.rstrip("/") + "/models",
                headers={"Authorization": f"Bearer {settings.tts_api_key}"},
                timeout=8,
            )
            rows.append(_ok("2. CosyVoice3 API", f"{settings.tts_base_url} 可访问，模型={settings.tts_model}") if r.ok
                        else _bad("2. CosyVoice3 API", f"HTTP {r.status_code}"))
        except Exception as exc:
            rows.append(_bad("2. CosyVoice3 API", str(exc)))

    root = Path(settings.musetalk_root)
    if not settings.musetalk_root:
        rows.append(_bad("3. MuseTalk 1.5", "MUSETALK_ROOT 未配置"))
    else:
        checks = [
            root.exists(),
            (root / "scripts" / "inference.py").exists(),
            Path(settings.musetalk_unet_path or root / "models/musetalkV15/unet.pth").exists(),
            Path(settings.musetalk_unet_config or root / "models/musetalkV15/musetalk.json").exists(),
            Path(settings.musetalk_whisper_dir or root / "models/whisper").exists(),
        ]
        rows.append(_ok("3. MuseTalk 1.5", f"root={root}; model/whisper/config=OK") if all(checks)
                    else _bad("3. MuseTalk 1.5", f"root={root}; model/whisper/config=INCOMPLETE"))

    rows.append("")
    rows.append("提示：系统检查只验证连接和文件，不会实际占用GPU跑视频。")
    return "\n".join(rows)
