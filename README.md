# FreeTalkVideo

Free/local-first talking-head video generator.

## MVP pipeline

1. Script input or topic -> local Qwen-compatible LLM
2. Script -> local CosyVoice-compatible TTS endpoint
3. TTS audio + avatar -> lip-sync adapter (MuseTalk)
4. Optional subtitles -> FFmpeg
5. Output 9:16 MP4

The project is intentionally modular. It does not depend on the compiled modules or proprietary services from KrLongAI.

## Quick start

Requirements: Python 3.10+, FFmpeg in PATH, NVIDIA GPU recommended, a local OpenAI-compatible LLM endpoint, and a local CosyVoice-compatible TTS endpoint.

Install with: python -m venv .venv, then activate it and run pip install -r requirements.txt. Start with python app.py.

Copy .env.example to .env and adjust endpoints.

### LLM

Default:
LLM_BASE_URL=http://127.0.0.1:11434/v1
LLM_MODEL=qwen3

If using Ollama, make sure the model is available locally.

### TTS

Default:
TTS_BASE_URL=http://127.0.0.1:9880/v1
TTS_MODEL=cosyvoice3

Point this at the local CosyVoice API wrapper you run.

### Lip sync

Set MUSETALK_ROOT to your local MuseTalk checkout. The adapter is isolated because MuseTalk launcher commands differ between releases.

Until configured, the app can generate a static-avatar video with the generated audio so the whole pipeline can be tested.

## Architecture

app.py -> core/pipeline.py -> adapters:
- core/llm.py
- core/tts.py
- core/lipsync.py
- core/video.py

outputs/ contains generated files and is ignored by git.

## Roadmap

- [x] Local-first project skeleton
- [x] Qwen-compatible script generation
- [x] CosyVoice-compatible TTS adapter
- [x] MuseTalk adapter boundary
- [x] FFmpeg composition and subtitles
- [ ] Automatic MuseTalk 1.5 command discovery
- [ ] Multi-avatar management
- [ ] Batch topic production
- [ ] Cover generation
- [ ] BGM ducking
- [ ] One-click Windows packaging
