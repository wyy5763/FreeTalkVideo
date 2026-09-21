from pathlib import Path
import base64
import sys
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
    model_dir = settings.cosyvoice_model_dir
    prompt_wav = settings.cosyvoice_prompt_wav
    prompt_text = settings.cosyvoice_prompt_text

    if not root.exists():
        raise TTSError("TTS_MODE=native 时必须配置 COSYVOICE_ROOT")
    if not model_dir:
        raise TTSError("TTS_MODE=native 时必须配置 COSYVOICE_MODEL_DIR")
    if not prompt_wav or not Path(prompt_wav).exists():
        raise TTSError("CosyVoice3 原生零样本模式需要 COSYVOICE_PROMPT_WAV")
    if not prompt_text:
        raise TTSError("CosyVoice3 原生零样本模式需要 COSYVOICE_PROMPT_TEXT")

    try:
        root_str = str(root.resolve())
        if root_str not in sys.path:
            sys.path.insert(0, root_str)
        import torch
        import torchaudio
        from cosyvoice.cli.cosyvoice import AutoModel

        model = AutoModel(model_dir=model_dir, fp16=settings.cosyvoice_fp16)
        chunks = []
        for item in model.inference_zero_shot(
            text,
            prompt_text,
            prompt_wav,
            stream=False,
            speed=speed,
        ):
            chunks.append(item["tts_speech"])
        if not chunks:
            raise TTSError("CosyVoice3 没有返回音频")
        audio = torch.cat(chunks, dim=1)
        torchaudio.save(str(output), audio.cpu(), model.sample_rate)
        return output
    except TTSError:
        raise
    except Exception as exc:
        raise TTSError(f"CosyVoice3 原生推理失败：{exc}") from exc

def synthesize(text: str, output: Path, voice: str | None = None, speed: float = 1.0) -> Path:
    output.parent.mkdir(parents=True, exist_ok=True)
    if settings.tts_mode == "native":
        return _native_synthesize(text, output, speed)
    return _api_synthesize(text, output, voice, speed)
