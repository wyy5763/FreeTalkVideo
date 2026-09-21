import json
import sys
from pathlib import Path

def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: python -m core.cosyvoice_worker request.json")

    request = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    root = Path(request["cosyvoice_root"])
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))

    import torch
    import torchaudio
    from cosyvoice.cli.cosyvoice import AutoModel

    model = AutoModel(
        model_dir=request["model_dir"],
        fp16=bool(request.get("fp16", True)),
    )
    chunks = []
    for item in model.inference_zero_shot(
        request["text"],
        request["prompt_text"],
        request["prompt_wav"],
        stream=False,
        speed=float(request.get("speed", 1.0)),
    ):
        chunks.append(item["tts_speech"])

    if not chunks:
        raise RuntimeError("CosyVoice3没有返回音频")

    audio = torch.cat(chunks, dim=1).cpu()
    output = Path(request["output"])
    output.parent.mkdir(parents=True, exist_ok=True)
    torchaudio.save(str(output), audio, model.sample_rate)

if __name__ == "__main__":
    main()
