# FreeTalkVideo

免费 / 本地模型驱动的中文口播视频工具，第一阶段针对 **Intel i7-9700 + 32GB RAM + 无 NVIDIA GPU** 做 CPU-only 适配。

## 第一阶段

**Qwen3 4B → CosyVoice3 0.5B → FFmpeg → 1080×1920 MP4**

MuseTalk 1.5 暂时关闭。以后增加 NVIDIA CUDA 显卡后再启用唇形同步。

## 当前代码已调整

- Qwen 默认模型：qwen3:4b
- MuseTalk 默认关闭：MUSETALK_ENABLED=false
- UI 默认不勾选 MuseTalk
- CosyVoice native 默认 FP16=false
- 输出目录可直接放 G 盘
- 系统检查区分 CPU-only 模式
- Windows 启动脚本检查 Ollama
- CPU-only 模式禁止误启动 MuseTalk

## 推荐 G 盘目录

G:\AI\FreeTalkVideo
G:\AI\Models\Fun-CosyVoice3-0.5B
G:\AI\CosyVoice
G:\AI\environments\cosyvoice

Qwen3 由 Ollama 管理，不需要复制进项目目录。

## 第一次运行

1. 安装 Python 3.10。
2. 安装 Ollama。
3. 执行：ollama pull qwen3:4b
4. 安装 FFmpeg，并确保 ffmpeg 在 PATH 中。
5. 双击 run.bat。
6. 首次启动会生成 .env。
7. 修改 .env 中的 CosyVoice 路径。
8. 打开网页，点击“系统检查”。
9. 上传一张正面人物图片。
10. 输入主题，先选择 15～20 秒。
11. 保持 MuseTalk 关闭。
12. 点击“开始生成”。

## Qwen3

默认连接 Ollama OpenAI-compatible API：

http://127.0.0.1:11434/v1

如果 ollama list 中模型名称不同，修改 LLM_MODEL。

## CosyVoice3

推荐 native 模式。需要单独准备 CosyVoice checkout、Fun-CosyVoice3-0.5B 模型、参考音频，以及对应的 Python 环境。

.env 关键配置：

TTS_MODE=native
COSYVOICE_ROOT=G:/AI/CosyVoice
COSYVOICE_PYTHON=G:/AI/environments/cosyvoice/Scripts/python.exe
COSYVOICE_MODEL_DIR=G:/AI/Models/Fun-CosyVoice3-0.5B
COSYVOICE_PROMPT_WAV=G:/AI/CosyVoice/asset/zero_shot_prompt.wav
COSYVOICE_FP16=false

也可以把 TTS_MODE 改成 api，连接已经运行的 OpenAI-compatible CosyVoice 服务。

## FFmpeg

推荐让 ffmpeg.exe 在 PATH 中；否则设置 FFMPEG_BIN 为完整路径。

## 预期输出

主题
→ Qwen3 4B
→ script.txt
→ CosyVoice3
→ speech.wav
→ FFmpeg
→ final.mp4

输出视频：1080×1920、H.264、AAC、MP4。

## 关于免费

FreeTalkVideo 本身不调用收费云 API。本阶段主要成本是模型下载、磁盘空间和 CPU 推理时间。CosyVoice 的安装依赖按照其官方项目准备。

## 后续 GPU 阶段

有 NVIDIA CUDA 显卡后再考虑 MuseTalk 1.5、FP16、GPU batch、精确 Whisper 字幕、多数字人、BGM 和批量任务。
