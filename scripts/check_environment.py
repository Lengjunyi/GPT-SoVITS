"""Exercise the installed inference/training dependencies without model downloads."""

import importlib
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "GPT_SoVITS")]


def main():
    for name in (
        "torch",
        "torchaudio",
        "librosa",
        "resampy",
        "pytorch_lightning",
        "gradio",
        "transformers",
        "peft",
        "onnxruntime",
        "pyopenjtalk",
        "jieba_fast",
        "faster_whisper",
        "funasr",
        "modelscope",
        "fast_langdetect",
        "module.models",
        "AR.models.t2s_lightning_module",
    ):
        importlib.import_module(name)
        print(f"OK: {name}", flush=True)

    import gradio as gr
    import numpy as np
    import soundfile as sf
    import torch
    import torchaudio
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from opencc import OpenCC
    from transformers import AutoModelForMaskedLM, AutoTokenizer, HubertModel

    for model_class in (AutoModelForMaskedLM, AutoTokenizer, HubertModel):
        assert callable(model_class.from_pretrained)
    assert OpenCC("t2s").convert("繁體中文") == "繁体中文"
    # This catches Gradio/Pydantic JSON-schema incompatibilities at runtime.
    with gr.Blocks() as demo:
        audio = gr.Audio(type="filepath")
        result = gr.Textbox()
        audio.change(lambda path: path or "", audio, result)
    demo.get_api_info()
    with TestClient(gr.mount_gradio_app(FastAPI(), demo, path="/")) as client:
        response = client.get("/")
        assert response.status_code == 200, response.text

    for executable in ("ffmpeg", "ffprobe"):
        if not shutil.which(executable):
            raise RuntimeError(f"Install {executable} and add it to PATH")
        subprocess.run([executable, "-version"], check=True, stdout=subprocess.DEVNULL)
    with tempfile.TemporaryDirectory() as directory:
        wav = Path(directory) / "test.wav"
        sf.write(wav, np.zeros(1600, dtype=np.float32), 16000)
        samples, rate = torchaudio.load(wav)
        assert rate == 16000 and samples.shape == (1, 1600)
        assert torch.isfinite(
            torchaudio.functional.resample(samples, rate, 32000)
        ).all()
    print("Environment checks passed (no pretrained weights loaded).")


if __name__ == "__main__":
    main()
