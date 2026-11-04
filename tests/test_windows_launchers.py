"""Native Windows regression tests. Run after installing English dependencies."""
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "English_Video_Transcriber_Windows"
TEST_TEMP = ROOT / ".validation"
TEST_TEMP.mkdir(exist_ok=True)


@unittest.skipUnless(os.name == "nt", "Windows launchers require Windows")
class WindowsLauncherTests(unittest.TestCase):
    def run_launcher(self, filename, media):
        if filename.endswith(".bat"):
            command = f'cmd.exe /d /s /c ""{PROJECT / filename}" "{media}""'
        else:
            command = ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass",
                       "-File", str(PROJECT / filename), "-MediaPath", str(media)]
        return subprocess.run(command, input="\n", text=True, capture_output=True, timeout=60)

    def test_powershell_reports_missing_input(self):
        with tempfile.TemporaryDirectory(prefix="launcher test ", dir=TEST_TEMP) as directory:
            result = self.run_launcher("transcribe.ps1", Path(directory) / "missing.wav")
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("File not found:", result.stdout + result.stderr)

    def test_bat_preserves_transcription_failure_status(self):
        with tempfile.TemporaryDirectory(prefix="launcher test ", dir=TEST_TEMP) as directory:
            result = self.run_launcher("Transcribe_Video.bat", Path(directory) / "missing.wav")
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("File not found:", result.stdout + result.stderr)

    def test_bat_without_argument_explains_drag_and_drop(self):
        result = subprocess.run(f'cmd.exe /d /s /c ""{PROJECT / "Transcribe_Video.bat"}""',
                                input="\n", text=True, capture_output=True, timeout=30)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("Drag", result.stdout)

    @unittest.skipUnless((PROJECT / ".venv/Scripts/python.exe").exists(), "Install English dependencies first")
    def test_powershell_dependency_check_survives_native_quoting(self):
        # A corrupt WAV must reach decoding rather than fail in python -c quoting.
        # Hugging Face offline mode prevents this negative test downloading a model.
        with tempfile.TemporaryDirectory(prefix="launcher test ", dir=TEST_TEMP) as directory:
            media = Path(directory) / "corrupt sample.wav"
            media.write_bytes(b"not a valid audio recording")
            with patch.dict(os.environ, {"HF_HUB_OFFLINE": "1"}):
                result = self.run_launcher("transcribe.ps1", media)
        self.assertNotIn("SyntaxError", result.stdout + result.stderr)
        self.assertIn("Loading model", result.stdout + result.stderr)
        self.assertNotEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
