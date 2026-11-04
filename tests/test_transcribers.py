"""Fast regression tests; model inference is replaced, file writing is real."""
import contextlib
import importlib.util
import io
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
TEST_TEMP = ROOT / ".validation"
TEST_TEMP.mkdir(exist_ok=True)
PROJECTS = {
    "english": ROOT / "English_Video_Transcriber_Windows",
    "bilingual": ROOT / "Bilingual_Subtitles_Windows_v3",
}


def load_script(version):
    spec = importlib.util.spec_from_file_location(version, PROJECTS[version] / "transcribe.py")
    module = importlib.util.module_from_spec(spec)
    # Importing a CLI should not require downloading a model to run these tests.
    with patch.dict(sys.modules, {"faster_whisper": SimpleNamespace(WhisperModel=None)}):
        spec.loader.exec_module(module)
    return module


class TranscriberTests(unittest.TestCase):
    def run_transcription(self, version, segments, stdout=None):
        module = load_script(version)
        temporary = tempfile.TemporaryDirectory(prefix="transcriber test ", dir=TEST_TEMP)
        self.addCleanup(temporary.cleanup)
        media = Path(temporary.name) / "English sample 中文.wav"
        media.write_bytes(b"test fixture; decoding is replaced by the model double")
        kwargs = {}

        class Model:
            def __init__(self, name, **options):
                kwargs["model"] = name
                kwargs["device"] = options

            def transcribe(self, path, **options):
                kwargs["transcribe"] = options
                return iter(segments), SimpleNamespace(duration=5.0, language="en")

        args = ["transcribe.py", str(media)]
        if version == "bilingual":
            args += ["--chinese", "simplified"]
        with patch.object(module, "WhisperModel", Model), patch.object(sys, "argv", args):
            with contextlib.redirect_stdout(stdout if stdout is not None else io.StringIO()):
                module.main()
        return (
            media.with_name(media.stem + "_transcript.txt").read_text(encoding="utf-8-sig"),
            media.with_name(media.stem + "_subtitles.srt").read_text(encoding="utf-8-sig"),
            kwargs,
        )

    def test_timestamp_rounding_and_hour_boundaries(self):
        for version in PROJECTS:
            module = load_script(version)
            for seconds, expected in [(0, "00:00:00,000"), (1.234, "00:00:01,234"),
                                      (59.9996, "00:01:00,000"), (3661.123, "01:01:01,123")]:
                with self.subTest(version=version, seconds=seconds):
                    self.assertEqual(module.srt_time(seconds), expected)

    def test_english_outputs_and_cpu_settings(self):
        txt, srt, options = self.run_transcription("english", [
            SimpleNamespace(start=0.0, end=1.25, text=" Hello world. "),
            SimpleNamespace(start=1.5, end=3.0, text=" A second sentence. "),
        ])
        self.assertEqual(txt, "Hello world.\nA second sentence.\n")
        self.assertEqual(srt, "1\n00:00:00,000 --> 00:00:01,250\nHello world.\n\n"
                             "2\n00:00:01,500 --> 00:00:03,000\nA second sentence.\n\n")
        self.assertEqual(options["device"], {"device": "cpu", "compute_type": "int8"})
        self.assertEqual(options["model"], "small.en")
        self.assertEqual(options["transcribe"]["language"], "en")
        self.assertTrue(options["transcribe"]["vad_filter"])

    def test_english_skips_blank_segments_without_numbering_gaps(self):
        txt, srt, _ = self.run_transcription("english", [
            SimpleNamespace(start=0.0, end=0.5, text=" "),
            SimpleNamespace(start=0.5, end=1.0, text="Hello."),
            SimpleNamespace(start=1.0, end=1.5, text=""),
            SimpleNamespace(start=1.5, end=2.0, text="Again."),
        ])
        self.assertEqual(txt, "Hello.\nAgain.\n")
        self.assertEqual(srt.splitlines()[0], "1")
        self.assertEqual(srt.splitlines()[4], "2")

    def test_english_logging_survives_legacy_console_encoding(self):
        buffer = io.BytesIO()
        console = io.TextIOWrapper(buffer, encoding="cp1252", errors="strict")
        self.addCleanup(console.close)
        txt, srt, _ = self.run_transcription("english", [
            SimpleNamespace(start=0.0, end=1.0, text="Hello."),
        ], stdout=console)
        self.assertEqual(txt, "Hello.\n")
        self.assertIn("00:00:01,000", srt)

    def test_empty_segments_create_empty_outputs(self):
        for version in PROJECTS:
            with self.subTest(version=version):
                txt, srt, _ = self.run_transcription(version, [])
                self.assertEqual((txt, srt), ("", ""))

    def test_bilingual_preserves_mixed_language_and_cpu_settings(self):
        txt, srt, options = self.run_transcription("bilingual", [
            SimpleNamespace(start=0.0, end=2.0, text=" 中文 project data。 "),
            SimpleNamespace(start=2.0, end=2.5, text=" "),
            SimpleNamespace(start=2.5, end=3.0, text="English result."),
        ])
        self.assertEqual(txt, "中文 project data。\nEnglish result.\n")
        self.assertEqual(srt.splitlines()[4], "2")
        self.assertEqual(options["device"], {"device": "cpu", "compute_type": "int8"})
        self.assertEqual(options["transcribe"]["task"], "transcribe")
        self.assertTrue(options["transcribe"]["multilingual"])
        self.assertFalse(options["transcribe"]["condition_on_previous_text"])

    def test_missing_input_exits_before_model_load(self):
        for version in PROJECTS:
            with self.subTest(version=version):
                module = load_script(version)
                with tempfile.TemporaryDirectory(dir=TEST_TEMP) as directory:
                    args = ["transcribe.py", str(Path(directory) / "missing.wav")]
                    with patch.object(sys, "argv", args), contextlib.redirect_stderr(io.StringIO()):
                        with self.assertRaises(SystemExit) as error:
                            module.main()
                    self.assertEqual(error.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
