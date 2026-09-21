import gradio as gr
from core.pipeline import create_video

def run(topic, avatar, style, seconds, speed, use_musetalk, add_srt):
    try:
        video, script, audio = create_video(
            topic, avatar, style, int(seconds), float(speed),
            use_musetalk, add_srt
        )
        return video, script, audio, "生成完成"
    except Exception as exc:
        return None, "", None, f"生成失败：{exc}"

with gr.Blocks(title="FreeTalkVideo") as demo:
    gr.Markdown(
        "# 🎙️ FreeTalkVideo\n"
        "免费/本地模型驱动的中文口播视频工具\n\n"
        "**Qwen → CosyVoice → MuseTalk → FFmpeg**"
    )

    with gr.Row():
        with gr.Column():
            topic = gr.Textbox(
                label="主题 / 口播稿",
                placeholder="输入主题，或输入完整口播稿。",
                lines=8,
            )
            avatar = gr.Image(label="头像图片", type="filepath")
            style = gr.Textbox(
                value="口语化、自然、有节奏，像一个真实的短视频博主",
                label="脚本风格",
            )
            seconds = gr.Slider(20, 180, value=60, step=5, label="目标时长（秒）")
            speed = gr.Slider(0.7, 1.3, value=1.0, step=0.05, label="语速")
            use_musetalk = gr.Checkbox(
                value=False,
                label="使用 MuseTalk 唇形同步（需本地安装）"
            )
            add_srt = gr.Checkbox(value=True, label="添加字幕")
            btn = gr.Button("🚀 开始生成", variant="primary")

        with gr.Column():
            video = gr.Video(label="最终视频")
            script = gr.Textbox(label="生成的口播稿", lines=12)
            audio = gr.Audio(label="语音")
            status = gr.Textbox(label="状态")

    btn.click(
        run,
        inputs=[topic, avatar, style, seconds, speed, use_musetalk, add_srt],
        outputs=[video, script, audio, status],
    )

if __name__ == "__main__":
    demo.launch()
