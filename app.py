import gradio as gr
from core.pipeline import create_video
from core.health import run_health_check

def run(topic, avatar, style, seconds, speed, use_musetalk, add_srt, voice):
    try:
        video, script, audio = create_video(
            topic, avatar, style, int(seconds), float(speed),
            use_musetalk, add_srt, voice
        )
        return video, script, audio, "生成完成"
    except Exception as exc:
        return None, "", None, f"生成失败：{exc}"

def health():
    return run_health_check()

with gr.Blocks(title="FreeTalkVideo") as demo:
    gr.Markdown(
        "# 🎙️ FreeTalkVideo\n"
        "免费/本地模型驱动的中文口播视频工具\n\n"
        "**1 Qwen → 2 CosyVoice3 → 3 MuseTalk 1.5 → 4 FFmpeg**"
    )

    with gr.Row():
        with gr.Column():
            topic = gr.Textbox(
                label="主题 / 口播稿",
                placeholder="输入主题，或输入完整口播稿。",
                lines=8,
            )
            avatar = gr.Image(label="数字人头像", type="filepath")
            style = gr.Textbox(
                value="口语化、自然、有节奏，像一个真实的短视频博主",
                label="脚本风格",
            )
            seconds = gr.Slider(20, 180, value=60, step=5, label="目标时长（秒）")
            speed = gr.Slider(0.7, 1.3, value=1.0, step=0.05, label="语速")
            voice = gr.Textbox(
                value="default",
                label="CosyVoice API voice（native模式忽略）",
            )
            use_musetalk = gr.Checkbox(
                value=True,
                label="使用 MuseTalk 1.5 唇形同步",
            )
            add_srt = gr.Checkbox(value=True, label="添加字幕")
            with gr.Row():
                btn = gr.Button("🚀 开始生成", variant="primary")
                check_btn = gr.Button("🔍 系统检查")

        with gr.Column():
            video = gr.Video(label="最终视频")
            script = gr.Textbox(label="生成的口播稿", lines=12)
            audio = gr.Audio(label="语音")
            status = gr.Textbox(label="状态", lines=8)

    btn.click(
        run,
        inputs=[topic, avatar, style, seconds, speed, use_musetalk, add_srt, voice],
        outputs=[video, script, audio, status],
    )
    check_btn.click(health, outputs=status)

if __name__ == "__main__":
    demo.launch()
