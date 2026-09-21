from pathlib import Path
import base64
import json
import subprocess
import tempfile
import requests
from .config import settings

class TTSError(RuntimeError):
    pass

def _api_synthesize(text: str, output: Path, voice: str | None, speed: float) -> Path:
    url = settings.tts_base_url.rstrip("/") + "/audio/speech"
    try:
        r = requests.post(
            url,
            headers={
                "Authorization": f"Bearer {settings.tts_api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": settings.tts_model,
                "input": text,
                "voice": voice or settings.tts_voice,
                "speed": speed,
                "response_format": "wav",
            },
            timeout=900,
        )
        r.raise_for_status()
        if "application/json" in r.headers.get("content-type", ""):
            payload = r.json()
            audio_b64 = payload.get("audio") or payload.get("data")
            if not audio_b64:
                raise TTSError("TTS返回JSON但没有audio/data字段")
            output.write_bytes(base64.b64decode(audio_b64))
        else:
            output.write_bytes(r.content)
        return output
    except TTSError:
        raise
    except Exception as exc:
        raise TTSError(f"CosyVoice API生成失败：{exc}") from exc

def _native_synthesize(text: str, output: Path, speed: float) -> Path:
    root = Path(settings.cosyvoice_root)
    if not root.exists():
        raise TTSError("TTS_MODE=native 时必须配置 COSYVOICE_ROOT")
    if not settings.cosyvoice_model_dir:
        raise TTSError("TTS_MODE=native 时必须配置 COSYVOICE_MODEL_DIR")
    if not settings.cosyvoice_prompt_wav or not Path(settings.cosyvoice_prompt_wav).exists():
        raise TTSError("CosyVoice3 原生零样本模式需要 COSYVOICE_PROMPT_WAV")
    if not settings.cosyvoice_prompt_text:
        raise TTSError("CosyVoice3 原生零样本模式需要 COSYVOICE_PROMPT_TEXT")

    request = {
        "cosyvoice_root": str(root.resolve()),
        "model_dir": settings.cosyvoice_model_dir,
        "prompt_wav": settings.cosyvoice_prompt_wav,
        "prompt_text": settings.cosyvoice_prompt_text,
        "text": text,
        "speed": speed,
        "output": str(output.resolve()),
        "fp16": settings.cosyvoice_fp16,
    }
    try:
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as f:
            json.dump(request, f, ensure_ascii=False)
            request_file = f.name
        p = subprocess.run(
            [settings.cosyvoice_python, "-m", "core.cosyvoice_worker", request_file],
            capture_output=True,
            text=True,
            timeout=900,
        )
        if p.returncode != 0:
            raise TTSError((p.stderr or p.stdout)[-8000:] or "CosyVoice native worker失败")
        if not output.exists():
            raise TTSError("CosyVoice native worker完成但没有生成WAV")
        return output
    except TTSError:
        raise
    except Exception as exc:
        raise TTSError(f"CosyVoice3 native worker失败：{exc}") from exc
    finally:
        try:
            Path(locals().get("request_file", "")).unlink(missing_ok=True)
        except Exception:
            pass

def synthesize(text: str, output: Path, voice: str | None = None, speed: float = 1.0) -> Path:
    output.parent.mkdir(parents=True, exist_ok=True)
    if settings.tts_mode == "native":
        return _native_synthesize(text, output, speed)
    return _api_synthesize(text, output, voice, speed)
