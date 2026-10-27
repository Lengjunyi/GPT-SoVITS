# 使用 uv 安装

简体中文 | [English](../en/uv.md)

请在仓库根目录执行下列命令。此方式使用独立的 `.venv` 环境、由
`.python-version` 默认选择的 Python 3.11，以及仓库中的 `uv.lock` 锁文件。
无需激活 Conda 环境。依赖配置允许使用 Python 3.10–3.12。

## 前置条件

- 安装 [uv](https://docs.astral.sh/uv/getting-started/installation/) 0.9.17 或更新版本。
  Apple Silicon 用户应使用原生 ARM64 版本的 uv 和 Python。混用 Intel 版
  Conda 中的 uv 与 ARM64 Python，可能编译出架构不兼容的扩展。
- 安装 FFmpeg（包含 `ffprobe`），并确保命令可在 `PATH` 中找到。
  macOS：`brew install ffmpeg`；Ubuntu/Debian：`sudo apt install ffmpeg`。
- 安装 C/C++ 编译器，用于构建 `pyopenjtalk`、`jieba-fast` 等扩展。
  macOS：`xcode-select --install`；Ubuntu/Debian：`sudo apt install build-essential`。
  Windows 源码构建需要安装带有 C++ 支持的 Visual Studio Build Tools。
  CMake 等 Python 构建依赖由 uv 自动安装。

## 安装依赖

```sh
uv sync --locked
uv run --locked python scripts/check_environment.py
```

环境检查包括模块导入、Gradio 页面 HTTP 响应、FFmpeg，以及 TorchAudio 的音频
读取和重采样，不会下载或加载预训练权重。

## 准备模型和语言资源

根据所选模型版本，按照现有的[预训练模型说明](README.md#预训练模型)准备权重，
包括共用的 HuBERT/BERT 模型和 G2PW。安装 Python 依赖不会自动下载模型权重。
此 uv 安装方式不新增模型下载器，也不替用户选择模型版本。请为所选权重预留数 GB
磁盘空间。

将英语和日语所需的词典下载到 uv 环境中：

```sh
uv run --locked python -m nltk.downloader -d .venv/nltk_data cmudict averaged_perceptron_tagger averaged_perceptron_tagger_eng
uv run --locked python -c "import pyopenjtalk; pyopenjtalk.g2p('こんにちは')"
```

这些命令需要联网。未提前安装日语词典时，首次使用也会触发下载。额外的 ASR 模型和
UVR5 权重继续按现有模型说明准备；语言识别或 ASR 功能首次使用时也可能下载资源。

## 启动

```sh
uv run --locked python webui.py
```

打开 <http://localhost:9874>，在 WebUI 中启动 TTS 推理界面（端口 9872）。
所有命令均应在仓库根目录执行。

## 适用范围和验证情况

当前应用配置在 macOS 上使用 CPU 进行推理和训练，即使 PyTorch 本身支持 MPS。
uv 配置的解析范围为 Apple Silicon、Linux x86_64/aarch64 和 Windows AMD64。
PyTorch 和 TorchAudio 使用 PyPI 提供的包，可用的加速后端取决于对应的 wheel。
如需指定 CUDA 或 ROCm 版本，请继续使用现有的设备专用安装器，不要在锁定的
`.venv` 环境中用 pip 替换 Torch 包。此配置不包含 Intel Mac，因为所选 PyTorch
版本不提供 macOS x86_64 wheel。

本次在 Apple Silicon、Python 3.11.13 上进行了本地验证。其他平台参与依赖解析，
但尚未进行运行时验证。`tools/portable_runtime.py` 中现有的 Windows 专用 FFmpeg
路径仍可能影响原生环境下的 API/快速推理；相关运行时修复与此依赖配置分开提交。

## 依赖约束的原因

- PyTorch/TorchAudio 固定为配套的 2.7.1，保留当前代码使用的音频加载接口，
  避免引入较新版本的 TorchCodec/FFmpeg 集成要求。
- NumPy 保持低于 2、Gradio 保持低于 5，与原有依赖要求一致。
- `huggingface-hub<1` 保留 Gradio 4 导入的 `HfFolder`。
- `starlette<1` 保留 Gradio 4 使用的模板渲染接口，否则 WebUI 会出现
  `TypeError: unhashable type: 'dict'`。
- `setuptools<81` 保留部分旧文本/ASR 依赖使用的 `pkg_resources`。
- ONNX Runtime 在 macOS 和 ARM 上使用 CPU 包，在 Linux/Windows x86_64 上使用
  GPU 包，保留原有选择方式并排除不支持的 macOS GPU 包。
- Faster Whisper 参与完整的依赖解析，不再需要原安装流程中的 `--no-deps` 步骤。
  OpenCC 使用可用的 wheel，此流程不强制从源码编译它。
- 显式声明 `resampy`，因为参考音频重采样代码会直接导入它，而当前 Librosa
  的默认安装不包含此依赖。

## 更新依赖

保留 `requirements.txt`、`extra-req.txt` 和原有安装器。修改共用依赖时，请同时更新
原有 requirements 文件和 `pyproject.toml`，然后重新生成锁文件并验证：

```sh
uv lock
uv sync --locked
uv pip check
uv run --locked python scripts/check_environment.py
uv run --locked python -m unittest test_api_v2_streaming test_official_streaming
```

请提交 `pyproject.toml`、`.python-version` 和 `uv.lock`，不要提交 `.venv` 或下载的
模型权重。需要单独升级某个包时，使用 `uv lock --upgrade-package NAME`。
