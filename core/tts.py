from pathlib import Path
import base64
import requests
from .config import settings

class TTSError(RuntimeError):
    pass

def synthesize(text: str, output: Path, voice: str | None = None, speed: float = 1.0) -> Path:
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
            timeout=600,
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
    except Exception as exc:
        raise TTSError(f"TTS生成失败，请检查CosyVoice本地服务：{exc}") from exc
