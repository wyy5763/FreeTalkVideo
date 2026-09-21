# FreeTalkVideo

免费 / 本地模型驱动的中文口播数字人视频工具。

核心链路：

**1. Qwen3 → 2. CosyVoice3 → 3. MuseTalk 1.5 → 4. FFmpeg → 9:16 MP4**

项目不依赖 KrLongAI 的闭源/编译模块，只借鉴工作流思路。

## 已完成

- [x] 1：Qwen3 本地脚本生成（OpenAI-compatible API）
- [x] 2：CosyVoice3 本地 TTS
  - API 模式：连接本地 OpenAI-compatible CosyVoice3 服务
  - native 模式：直接从本机 CosyVoice3 checkout 加载模型
  - 支持 CosyVoice3 zero-shot 参考音频
- [x] 3：MuseTalk 1.5 真正推理链路
  - 头像图片直接作为 MuseTalk 输入
  - 自动生成 task.yaml
  - 自动调用 `python -m scripts.inference`
  - 自动寻找输出 MP4
  - 支持 v15 / GPU / FP16 / batch size
- [x] 4：FFmpeg 视频合成
  - 1080x1920 竖屏
  - 音频合成
  - SRT 字幕烧录
- [x] 系统检查
- [x] Windows `run.bat`

MuseTalk 官方当前的 1.5 normal inference 使用 `scripts.inference`、`--inference_config`、`--unet_model_path`、`--unet_config`、`--version v15` 等参数；本项目已经按这个接口实现适配。

## 目录

```
FreeTalkVideo/
├─ app.py
├─ run.bat
├─ requirements.txt
├─ .env.example
├─ core/
│  ├─ config.py
│  ├─ health.py
│  ├─ llm.py
│  ├─ tts.py
│  ├─ lipsync.py
│  ├─ video.py
│  ├─ subtitles.py
│  └─ pipeline.py
└─ outputs/
```

## Windows 快速启动

安装 Python 3.10+ 和 FFmpeg。

然后双击：

```
run.bat
```

第一次启动会创建 `.venv`、安装项目依赖，并自动生成 `.env`。

## 1. Qwen3

默认按 Ollama 的 OpenAI-compatible 接口连接：

```env
LLM_BASE_URL=http://127.0.0.1:11434/v1
LLM_API_KEY=ollama
LLM_MODEL=qwen3
```

先确认本机 Qwen3 可以被调用，然后启动 FreeTalkVideo。

如果你的 Qwen3 是 vLLM、SGLang 或其他 OpenAI-compatible 服务，只需要修改 `LLM_BASE_URL` 和 `LLM_MODEL`。

## 2. CosyVoice3

### 方案 A：CosyVoice3 API

这是最简单的方式。

配置：

```env
TTS_MODE=api
TTS_BASE_URL=http://127.0.0.1:8080/v1
TTS_MODEL=cosyvoice3
TTS_VOICE=default
```

本项目会调用：

```
POST /v1/audio/speech
```

因此可以连接任何提供 OpenAI-compatible TTS 接口的本地 CosyVoice3 服务。

### 方案 B：CosyVoice3 native

不启动额外 API 服务，直接加载本地 CosyVoice3。

```env
TTS_MODE=native
COSYVOICE_ROOT=D:/AI/CosyVoice
COSYVOICE_MODEL_DIR=D:/AI/CosyVoice/pretrained_models/Fun-CosyVoice3-0.5B
COSYVOICE_PROMPT_WAV=D:/AI/CosyVoice/asset/zero_shot_prompt.wav
COSYVOICE_PROMPT_TEXT=You are a helpful assistant.<|endofprompt|>希望你以后能够做的比我还好呦。
COSYVOICE_FP16=true
```

native 模式使用 CosyVoice3 的 `AutoModel(...).inference_zero_shot(...)`，生成 WAV 后交给 MuseTalk。

注意：CosyVoice 本身的 PyTorch / CUDA / 模型依赖可以安装在独立环境中。将 `COSYVOICE_ROOT` 指向 CosyVoice checkout，并将 `COSYVOICE_PYTHON` 指向 CosyVoice 环境的 Python；FreeTalkVideo 会通过独立 worker 进程调用 CosyVoice3，因此不要求把 CosyVoice 和主程序依赖强行装进同一个环境。MuseTalk 同样可以通过 `MUSETALK_PYTHON` 使用独立环境。

## 3. MuseTalk 1.5

下载并配置官方 MuseTalk 1.5 后，至少需要：

```
models/musetalkV15/unet.pth
models/musetalkV15/musetalk.json
models/whisper/
scripts/inference.py
```

配置：

```env
MUSETALK_ROOT=D:/AI/MuseTalk
MUSETALK_PYTHON=D:/AI/musetalk/.venv/Scripts/python.exe
MUSETALK_VERSION=v15
MUSETALK_GPU_ID=0
MUSETALK_BATCH_SIZE=8
MUSETALK_FLOAT16=true
```

项目会自动生成：

```
inference_config
    ↓
MuseTalk scripts.inference
    ↓
results/v15/*.mp4
    ↓
FreeTalkVideo 输出目录
```

MuseTalk 1.5 可以直接把图片作为输入，因此用户只需要上传一张正面数字人头像，不需要提前制作一段静态视频。

## 4. FFmpeg

确认：

```bash
ffmpeg -version
```

如果 FFmpeg 不在 PATH：

```env
FFMPEG_BIN=D:/ffmpeg/bin/ffmpeg.exe
```

MuseTalk 如果自己需要独立的 FFmpeg，也可以设置：

```env
MUSETALK_FFMPEG_PATH=D:/ffmpeg/bin
```

## 一次完整生成

打开：

```bash
python app.py
```

网页中：

1. 输入主题，例如：`为什么很多人明明很努力，却还是赚不到钱？`
2. 上传一张正面头像
3. 勾选 MuseTalk 1.5
4. 点击「系统检查」
5. 检查 1/2/3/4 全部通过
6. 点击「开始生成」

实际执行：

```
主题
 ↓
Qwen3
 ↓
口播稿
 ↓
CosyVoice3
 ↓
speech.wav
 ↓
MuseTalk 1.5
 ↓
talking.mp4
 ↓
FFmpeg + SRT
 ↓
final.mp4 1080x1920
```

## 关于显卡

这条链路是本地 AI 推理，Qwen3、CosyVoice3、MuseTalk 都可能占用显存。

尤其 MuseTalk 1.5 和 CosyVoice3 都建议使用 NVIDIA CUDA 环境。

如果显存不足：

- Qwen3 使用更小的本地模型或量化模型
- CosyVoice3 使用 FP16
- MuseTalk 使用 FP16
- MuseTalk 降低 batch size，例如 4 / 2 / 1
- 不要同时在同一 GPU 上启动多个重量级服务

## 当前已知限制

- 字幕目前根据标点和音频总时长估算，不是 Whisper 逐词时间戳。
- MuseTalk 的人脸检测需要输入头像清晰、正面程度合适。
- CosyVoice native 模式依赖 CosyVoice 自己的 Python/CUDA 环境。
- 第一次 MuseTalk 推理会明显慢于后续推理，因为模型加载和人脸预处理需要时间。

## 下一阶段

- [ ] Whisper / faster-whisper 精确字幕
- [ ] 多数字人头像管理
- [ ] 多声音 / 参考音频管理
- [ ] 批量生成多个主题
- [ ] BGM 自动混音和人声压低
- [ ] 自动生成短视频封面
- [ ] 任务队列 / 进度条
- [ ] Windows 一键安装模型环境
- [ ] GPU 显存检测与自动降级
