"""Check Git's actual ignore decisions without creating private files."""
from pathlib import Path
import shutil
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(shutil.which("git") and (ROOT / ".git").exists(), "Requires a Git checkout")
class RepositoryHygieneTests(unittest.TestCase):
    def ignored(self, path):
        return subprocess.run(["git", "check-ignore", "--no-index", "-q", "--", path],
                              cwd=ROOT, capture_output=True).returncode == 0

    def test_recordings_outputs_environments_and_secrets_are_ignored(self):
        for path in ["meeting.mp4", "audio.WAV", "interview.mp3", "nested/sample.m4a",
                     "nested/clip.flac", "clip_subtitles.srt", "clip_transcript.txt",
                     "English_Video_Transcriber_Windows/.venv/pyvenv.cfg",
                     "Bilingual_Subtitles_Windows_v3/.venv/Scripts/python.exe",
                     "models/weights.bin", ".cache/huggingface/config.json",
                     ".env", "credentials.json", "private.key", ".validation/results.json"]:
            with self.subTest(path=path):
                self.assertTrue(self.ignored(path), path)

    def test_source_and_intended_text_documents_can_be_uploaded(self):
        for path in ["README.md", "tests/test_transcribers.py",
                     "English_Video_Transcriber_Windows/transcribe.py",
                     "English_Video_Transcriber_Windows/Transcribe_Video.bat",
                     "English_Video_Transcriber_Windows/requirements.txt",
                     "Bilingual_Subtitles_Windows_v3/requirements.txt",
                     "Bilingual_Subtitles_Windows_v3/README_使用說明_繁體中文.txt"]:
            with self.subTest(path=path):
                self.assertFalse(self.ignored(path), path)


if __name__ == "__main__":
    unittest.main()
