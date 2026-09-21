from dataclasses import dataclass
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class Settings:
    llm_base_url: str = os.getenv("LLM_BASE_URL", "http://127.0.0.1:11434/v1")
    llm_api_key: str = os.getenv("LLM_API_KEY", "ollama")
    llm_model: str = os.getenv("LLM_MODEL", "qwen3")
    tts_base_url: str = os.getenv("TTS_BASE_URL", "http://127.0.0.1:9880/v1")
    tts_api_key: str = os.getenv("TTS_API_KEY", "local")
    tts_model: str = os.getenv("TTS_MODEL", "cosyvoice3")
    tts_voice: str = os.getenv("TTS_VOICE", "default")
    musetalk_root: str = os.getenv("MUSETALK_ROOT", "")
    musetalk_python: str = os.getenv("MUSETALK_PYTHON", "python")
    ffmpeg_bin: str = os.getenv("FFMPEG_BIN", "ffmpeg")
    output_dir: Path = Path(os.getenv("OUTPUT_DIR", "outputs"))

    def ensure_dirs(self):
        self.output_dir.mkdir(parents=True, exist_ok=True)

settings = Settings()
settings.ensure_dirs()
