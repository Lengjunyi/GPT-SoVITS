"""Download the default v2Pro models and text resources after `uv sync`."""

import argparse
import os
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# Pin model assets independently of the Python dependency lockfile.
MODEL_REVISION = "8f8857563c040d542de108a2c18b0425abd6c9c5"
G2PW_REVISION = "0c47645e02a7bc3688d7b263b0042c81e3cd82cd"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--skip-models",
        action="store_true",
        help="Only install NLTK and Japanese dictionaries",
    )
    args = parser.parse_args()
    os.chdir(ROOT)

    import nltk
    import pyopenjtalk
    from huggingface_hub import hf_hub_download, snapshot_download

    nltk_dir = Path(sys.prefix) / "nltk_data"
    for resource in (
        "cmudict",
        "averaged_perceptron_tagger",
        "averaged_perceptron_tagger_eng",
    ):
        nltk.download(resource, download_dir=str(nltk_dir), raise_on_error=True)
    # The public API downloads the dictionary on its first use.
    pyopenjtalk.g2p("こんにちは")

    if args.skip_models:
        return
    snapshot_download(
        "lj1995/GPT-SoVITS",
        revision=MODEL_REVISION,
        local_dir=ROOT / "GPT_SoVITS/pretrained_models",
        allow_patterns=[
            "chinese-hubert-base/*",
            "chinese-roberta-wwm-ext-large/*",
            "s1v3.ckpt",
            "v2Pro/s2Gv2Pro.pth",
            "v2Pro/s2Dv2Pro.pth",
            "sv/*",
        ],
        max_workers=2,
    )
    text_dir = ROOT / "GPT_SoVITS/text"
    if not (text_dir / "G2PWModel/g2pW.onnx").is_file():
        archive = hf_hub_download(
            "XXXXRT/GPT-SoVITS-Pretrained",
            "G2PWModel.zip",
            revision=G2PW_REVISION,
            local_dir=ROOT / ".cache/setup",
        )
        with zipfile.ZipFile(archive) as models:
            for entry in models.infolist():
                if not (text_dir / entry.filename).resolve().is_relative_to(text_dir):
                    raise ValueError(f"Unsafe archive path: {entry.filename}")
            models.extractall(text_dir)
    print("Assets ready. Start the WebUI with: uv run --locked python webui.py")


if __name__ == "__main__":
    main()
