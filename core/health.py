import shutil
import platform
from pathlib import Path
import requests
from .config import settings

def _ok(name, detail): return f"✅ {name}: {detail}"
def _bad(name, detail): return f"❌ {name}: {detail}"
def _warn(name, detail): return f"⚠️ {name}: {detail}"

def run_health_check() -> str:
    rows = [
        "FreeTalkVideo CPU 模式系统检查",
        "=" * 40,
        f"平台：{platform.system()} {platform.release()}",
        "硬件策略：无 NVIDIA CUDA 时走 CPU；MuseTalk 默认关闭。",
        ""
    ]
    ffmpeg = shutil.which(settings.ffmpeg_bin)
    rows.append(_ok("4. FFmpeg", ffmpeg) if ffmpeg else _bad("4. FFmpeg", f"找不到 {settings.ffmpeg_bin}"))

    try:
        r = requests.get(settings.llm_base_url.rstrip("/") + "/models",
                         headers={"Authorization": f"Bearer {settings.llm_api_key}"}, timeout=8)
        rows.append(_ok("1. Qwen3/LLM", f"{settings.llm_base_url} 可访问；模型={settings.llm_model}") if r.ok
                    else _bad("1. Qwen3/LLM", f"HTTP {r.status_code}"))
        try:
            ids = {m.get("id") for m in r.json().get("data", []) if isinstance(m, dict)}
            if ids and settings.llm_model not in ids:
                rows.append(_warn("Qwen3 模型", f"接口可用但未发现 {settings.llm_model}；执行 ollama pull {settings.llm_model}"))
        except Exception:
            pass
    except Exception as exc:
        rows.append(_bad("1. Qwen3/LLM", f"{settings.llm_base_url} 不可访问：{exc}"))

    if settings.tts_mode == "native":
        root = Path(settings.cosyvoice_root)
        model = Path(settings.cosyvoice_model_dir)
        prompt = Path(settings.cosyvoice_prompt_wav)
        ok = root.exists() and model.exists() and prompt.exists()
        rows.append(_ok("2. CosyVoice3 native", "root/model/参考音频均存在") if ok
                    else _bad("2. CosyVoice3 native", f"root={root.exists()}, model={model.exists()}, prompt_wav={prompt.exists()}"))
        if settings.cosyvoice_fp16:
            rows.append(_warn("CosyVoice3", "CPU 模式建议 COSYVOICE_FP16=false"))
    else:
        try:
            r = requests.get(settings.tts_base_url.rstrip("/") + "/models",
                             headers={"Authorization": f"Bearer {settings.tts_api_key}"}, timeout=8)
            rows.append(_ok("2. CosyVoice3 API", f"{settings.tts_base_url} 可访问；模型={settings.tts_model}") if r.ok
                        else _bad("2. CosyVoice3 API", f"HTTP {r.status_code}"))
        except Exception as exc:
            rows.append(_bad("2. CosyVoice3 API", f"{settings.tts_base_url} 不可访问：{exc}"))

    if not settings.musetalk_enabled:
        rows.append(_warn("3. MuseTalk 1.5", "已按 CPU-only 方案关闭，不启动。"))
    else:
        root = Path(settings.musetalk_root)
        checks = [
            root.exists(),
            (root / "scripts" / "inference.py").exists(),
            Path(settings.musetalk_unet_path or root / "models/musetalkV15/unet.pth").exists(),
            Path(settings.musetalk_unet_config or root / "models/musetalkV15/musetalk.json").exists(),
            Path(settings.musetalk_whisper_dir or root / "models/whisper").exists()
        ]
        rows.append(_ok("3. MuseTalk 1.5", "root/model/whisper/config=OK") if all(checks)
                    else _bad("3. MuseTalk 1.5", "配置不完整"))

    rows += ["", "验收：1/2/4 可用即可生成第一版静态口播 MP4；3 在 CPU-only 模式下显示“已关闭”。",
             "建议首次测试：15～20秒、关闭 MuseTalk。"]
    return "\n".join(rows)
