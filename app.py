import gradio as gr
from core.pipeline import create_video
from core.health import run_health_check
from core.config import settings

def run(topic, avatar, style, seconds, speed, use_musetalk, add_srt, voice):
    try:
        video, script, audio = create_video(topic, avatar, style, int(seconds), float(speed), use_musetalk, add_srt, voice)
        return video, script, audio, "✅ 生成完成\n\n已输出 1080×1920 MP4。"
    except Exception as exc:
        return None, "", None, f"❌ 生成失败：{exc}"

def health():
    return run_health_check()

with gr.Blocks(title="FreeTalkVideo") as demo:
    gr.Markdown("# 🎙️ FreeTalkVideo\n免费 / 本地模型 / CPU 友好版中文口播视频工具\n\n**CPU 路线：Qwen3 4B → CosyVoice3 0.5B → FFmpeg → 1080×1920 MP4**")
    gr.Markdown("⚠️ 当前电脑无 NVIDIA GPU：**MuseTalk 已默认关闭**。先跑通“脚本 → 语音 → 静态口播视频”，以后有 NVIDIA GPU 再启用唇形同步。")
    with gr.Row():
        with gr.Column():
            topic = gr.Textbox(label="主题 / 口播稿", placeholder="输入主题，或输入完整口播稿。", lines=8)
            avatar = gr.Image(label="数字人头像", type="filepath")
            style = gr.Textbox(value="口语化、自然、有节奏，像一个真实的短视频博主", label="脚本风格")
            seconds = gr.Slider(15, 120, value=20, step=5, label="目标时长（秒）")
            speed = gr.Slider(0.7, 1.3, value=1.0, step=0.05, label="语速")
            voice = gr.Textbox(value="default", label="CosyVoice voice（API模式）")
            use_musetalk = gr.Checkbox(value=False, label="使用 MuseTalk 1.5（CPU模式请勿勾选）", interactive=settings.musetalk_enabled)
            add_srt = gr.Checkbox(value=True, label="添加字幕")
            with gr.Row():
                btn = gr.Button("🚀 开始生成", variant="primary")
                check_btn = gr.Button("🔍 系统检查")
        with gr.Column():
            video = gr.Video(label="最终视频")
            script = gr.Textbox(label="生成的口播稿", lines=12)
            audio = gr.Audio(label="语音")
            status = gr.Textbox(label="状态", lines=8)
    btn.click(run, inputs=[topic, avatar, style, seconds, speed, use_musetalk, add_srt, voice], outputs=[video, script, audio, status])
    check_btn.click(health, outputs=status)

if __name__ == "__main__":
    demo.launch()
