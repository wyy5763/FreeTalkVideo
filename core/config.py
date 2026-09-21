from dataclasses import dataclass
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

def _bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}

def _int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except ValueError:
        return default

@dataclass(frozen=True)
class Settings:
    llm_base_url: str = os.getenv("LLM_BASE_URL", "http://127.0.0.1:11434/v1")
    llm_api_key: str = os.getenv("LLM_API_KEY", "ollama")
    llm_model: str = os.getenv("LLM_MODEL", "qwen3:4b")
    tts_mode: str = os.getenv("TTS_MODE", "native").lower()
    tts_base_url: str = os.getenv("TTS_BASE_URL", "http://127.0.0.1:8080/v1")
    tts_api_key: str = os.getenv("TTS_API_KEY", "local")
    tts_model: str = os.getenv("TTS_MODEL", "cosyvoice3")
    tts_voice: str = os.getenv("TTS_VOICE", "default")
    cosyvoice_root: str = os.getenv("COSYVOICE_ROOT", "")
    cosyvoice_python: str = os.getenv("COSYVOICE_PYTHON", "python")
    cosyvoice_model_dir: str = os.getenv("COSYVOICE_MODEL_DIR", "")
    cosyvoice_prompt_wav: str = os.getenv("COSYVOICE_PROMPT_WAV", "")
    cosyvoice_prompt_text: str = os.getenv("COSYVOICE_PROMPT_TEXT", "")
    cosyvoice_fp16: bool = _bool("COSYVOICE_FP16", False)
    musetalk_enabled: bool = _bool("MUSETALK_ENABLED", False)
    musetalk_root: str = os.getenv("MUSETALK_ROOT", "")
    musetalk_python: str = os.getenv("MUSETALK_PYTHON", "python")
    musetalk_version: str = os.getenv("MUSETALK_VERSION", "v15")
    musetalk_gpu_id: int = _int("MUSETALK_GPU_ID", 0)
    musetalk_batch_size: int = _int("MUSETALK_BATCH_SIZE", 1)
    musetalk_float16: bool = _bool("MUSETALK_FLOAT16", False)
    musetalk_whisper_dir: str = os.getenv("MUSETALK_WHISPER_DIR", "")
    musetalk_unet_path: str = os.getenv("MUSETALK_UNET_PATH", "")
    musetalk_unet_config: str = os.getenv("MUSETALK_UNET_CONFIG", "")
    musetalk_ffmpeg_path: str = os.getenv("MUSETALK_FFMPEG_PATH", "")
    ffmpeg_bin: str = os.getenv("FFMPEG_BIN", "ffmpeg")
    output_dir: Path = Path(os.getenv("OUTPUT_DIR", "outputs"))
    def ensure_dirs(self):
        self.output_dir.mkdir(parents=True, exist_ok=True)

settings = Settings()
settings.ensure_dirs()
