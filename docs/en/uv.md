# Installation with uv

Run the commands below from the repository root. This workflow uses an isolated
`.venv`, Python 3.11 (selected by `.python-version`), and the committed `uv.lock`.
It does not require activating a Conda environment. Python 3.10–3.12 are allowed.

## Prerequisites

- Install [uv](https://docs.astral.sh/uv/getting-started/installation/) 0.9.17 or newer.
  On Apple Silicon, use the native ARM64 version of uv and Python; mixing an Intel
  Conda uv with ARM64 Python can build incompatible native extensions.
- Install FFmpeg (including `ffprobe`) and put it on `PATH`.
  On macOS: `brew install ffmpeg`; on Ubuntu/Debian: `sudo apt install ffmpeg`.
- Install a C/C++ compiler for `pyopenjtalk` and `jieba-fast`.
  On macOS: `xcode-select --install`; on Ubuntu/Debian: `sudo apt install build-essential`.
  Windows source builds require Visual Studio Build Tools with C++ support.
  uv supplies Python build dependencies such as CMake automatically.

## Install and start

```sh
uv sync --locked
uv run --locked python scripts/check_environment.py
uv run --locked python scripts/setup_assets.py
uv run --locked python webui.py
```

Open <http://localhost:9874>. In the WebUI, start the TTS inference interface
(port 9872). The default model is v2Pro. The asset setup downloads its GPT and
SoVITS weights, speaker encoder, HuBERT, Chinese BERT, G2PW, and English/Japanese
text resources. Allow several GB of disk space and an internet connection.
The main model snapshot and G2PW archive revision are pinned in `scripts/setup_assets.py`; model files are
not part of the Python lockfile or Git commits. Re-running setup reuses existing
downloads. To install only the language dictionaries, use `--skip-models`.

Additional model versions, ASR models, and UVR5 weights remain separate downloads;
see [Pretrained Models](../../README.md#pretrained-models). The application may
download language detection or ASR assets when first used.

macOS uses CPU inference/training under the current application configuration,
even though PyTorch supports MPS. The uv configuration targets Apple Silicon,
Linux x86_64/aarch64, and Windows AMD64. PyTorch and TorchAudio come from PyPI;
the available accelerator backend depends on those wheels. For a specific CUDA
or ROCm build, retain the existing device-specific installers rather than mixing
pip-installed Torch packages into the locked `.venv`. Intel Macs are excluded
because this PyTorch version has no macOS x86_64 wheels.

Local validation was performed on Apple Silicon with Python 3.11.13. Other
platforms are included in dependency resolution but have not been runtime-tested
as part of this migration.

## Why these constraints exist

- PyTorch/TorchAudio 2.7.1 stay paired and retain the audio loading APIs used here,
  without requiring the TorchCodec/FFmpeg integration introduced in newer releases.
- NumPy stays below 2, and Gradio stays below 5, matching the legacy requirements.
- `huggingface-hub<1` retains `HfFolder`, imported by Gradio 4.
- `starlette<1` retains the template rendering API used by Gradio 4; without it,
  the WebUI fails with `TypeError: unhashable type: 'dict'`.
- `setuptools<81` retains `pkg_resources` for older text/ASR dependencies.
- ONNX Runtime uses CPU wheels on macOS and ARM, and GPU wheels on Linux/Windows
  x86_64, preserving the existing selection while excluding unsupported macOS GPU wheels.
- Faster Whisper participates in resolution, replacing the legacy `--no-deps`
  installation step. OpenCC uses available wheels; it need not be compiled from
  source for this workflow.
- `resampy` is explicit because reference-audio resampling imports it directly;
  current Librosa installations do not install it by default.

`requirements.txt`, `extra-req.txt`, and the existing installers remain available.
When changing shared dependencies, update both the legacy requirements and
`pyproject.toml`. Then regenerate and validate the lockfile:

```sh
uv lock
uv sync --locked
uv pip check
uv run --locked python scripts/check_environment.py
uv run --locked python -m unittest test_portable_runtime test_api_v2_streaming test_official_streaming
```

Commit `pyproject.toml`, `.python-version`, and `uv.lock`, never `.venv` or downloaded
weights. Use `uv lock --upgrade-package NAME` for deliberate package updates.
