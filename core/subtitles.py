from pathlib import Path
import wave
import contextlib

def write_basic_srt(text: str, audio: Path, output: Path):
    duration = 60.0
    try:
        with contextlib.closing(wave.open(str(audio), "rb")) as wf:
            duration = wf.getnframes() / float(wf.getframerate())
    except Exception:
        pass

    chunks = [
        x.strip()
        for x in text.replace("。", "。|").replace("！", "！|").replace("？", "？|").split("|")
        if x.strip()
    ] or [text.strip()]

    chunk_duration = max(duration / len(chunks), 1.0)

    def stamp(seconds):
        ms = int(seconds * 1000)
        h, ms = divmod(ms, 3600000)
        m, ms = divmod(ms, 60000)
        s, ms = divmod(ms, 1000)
        return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

    lines = []
    for i, chunk in enumerate(chunks, 1):
        start = (i - 1) * chunk_duration
        end = min(i * chunk_duration, duration)
        lines += [str(i), f"{stamp(start)} --> {stamp(end)}", chunk, ""]
    output.write_text("\n".join(lines), encoding="utf-8-sig")
    return output
