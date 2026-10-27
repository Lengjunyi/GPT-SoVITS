"""Native installations must not require the Windows portable bundle."""

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools import portable_runtime as runtime


class PortableRuntimeTests(unittest.TestCase):
    def test_system_ffmpeg_without_bundle(self):
        with (
            patch.object(runtime.shutil, "which", return_value="/usr/bin/ffmpeg"),
            patch.object(Path, "is_file", return_value=False),
        ):
            self.assertEqual(runtime._media_executable("ffmpeg"), "/usr/bin/ffmpeg")

    def test_windows_bundle_takes_precedence(self):
        with (
            patch.object(runtime.os, "name", "nt"),
            patch.object(Path, "is_file", return_value=True),
        ):
            self.assertEqual(
                runtime._media_executable("ffmpeg"),
                str(runtime.RUNTIME_DIR / "ffmpeg.exe"),
            )

    def test_activation_preserves_user_nltk_data(self):
        with tempfile.TemporaryDirectory() as directory:
            bundled = Path(directory)
            (bundled / "nltk_data").mkdir()
            with (
                patch.object(runtime, "RUNTIME_DIR", bundled),
                patch.object(runtime, "_ACTIVE", False),
                patch.object(runtime, "_prepare_dlls"),
                patch.object(runtime, "prepare_transformers_flash_attention"),
                patch.dict(os.environ, {"NLTK_DATA": "/custom/nltk_data"}),
                patch.object(runtime.sys, "path", runtime.sys.path.copy()),
            ):
                runtime.activate()
                self.assertEqual(os.environ["NLTK_DATA"], "/custom/nltk_data")


if __name__ == "__main__":
    unittest.main()
