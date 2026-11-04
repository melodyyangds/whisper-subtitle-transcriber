"""Run actual CPU inference and validate outputs; no recordings are bundled.

Use the English virtual environment's Python. On Windows, also exercises the
PowerShell and BAT launchers. Generated fixtures stay in ignored .validation/.
"""
import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

import av

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "English_Video_Transcriber_Windows"
TIMING = re.compile(r"^(\d{2,}):([0-5]\d):([0-5]\d),(\d{3}) --> "
                    r"(\d{2,}):([0-5]\d):([0-5]\d),(\d{3})$")


def validate(media, duration, expected):
    text = media.with_name(media.stem + "_transcript.txt").read_text(encoding="utf-8-sig")
    subtitles = media.with_name(media.stem + "_subtitles.srt").read_text(encoding="utf-8-sig")
    blocks = subtitles.strip().split("\n\n")
    lines = []
    previous_start = -1
    for index, block in enumerate(blocks, start=1):
        parts = block.splitlines()
        if len(parts) < 3 or parts[0] != str(index):
            raise ValueError("Invalid SRT cue numbering or empty cue")
        match = TIMING.fullmatch(parts[1])
        if not match:
            raise ValueError("Invalid SRT timestamp")
        h, m, s, ms, eh, em, es, ems = map(int, match.groups())
        start = h * 3600 + m * 60 + s + ms / 1000
        end = eh * 3600 + em * 60 + es + ems / 1000
        if not (previous_start <= start < end <= duration + 1):
            raise ValueError("SRT times are out of order or outside the sample duration")
        previous_start = start
        lines.append(" ".join(parts[2:]))
    if " ".join(text.split()) != " ".join(" ".join(lines).split()):
        raise ValueError("TXT and SRT transcription text disagree")
    if not text.strip():
        raise ValueError("No speech recognized")
    for phrase in expected:
        if phrase.casefold() not in text.casefold():
            raise ValueError(f"Expected phrase was not recognized: {phrase}")
    return {"cues": len(blocks), "valid_timestamps": True, "matching_txt": True,
            "expected_phrases_found": True}


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="backslashreplace")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sample", type=Path, help="A short, non-sensitive English speech recording")
    parser.add_argument("--expect", action="append", default=[], help="Phrase required in the transcript")
    args = parser.parse_args()
    source = args.sample.resolve(strict=True)
    with av.open(str(source)) as container:
        duration = container.duration / av.time_base
    local = ROOT / ".validation"
    local.mkdir(exist_ok=True)
    run = Path(tempfile.mkdtemp(prefix="live smoke ", dir=local))
    routes = ["python", "powershell", "bat"] if os.name == "nt" else ["python"]
    results = {}
    for route in routes:
        folder = run / route
        folder.mkdir()
        media = folder / ("English speech sample" + source.suffix)
        shutil.copyfile(source, media)
        if route == "python":
            command = [sys.executable, str(PROJECT / "transcribe.py"), str(media)]
        elif route == "powershell":
            command = ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass",
                       "-File", str(PROJECT / "transcribe.ps1"), "-MediaPath", str(media)]
        else:
            command = f'cmd.exe /d /s /c ""{PROJECT / "Transcribe_Video.bat"}" "{media}""'
        env = dict(os.environ, PYTHONIOENCODING="utf-8")
        process = subprocess.run(command, input="\n", text=True, encoding="utf-8",
                                 errors="replace", capture_output=True, env=env, timeout=600)
        (folder / "process.log").write_text(process.stdout + process.stderr, encoding="utf-8")
        if process.returncode:
            raise RuntimeError(f"{route} failed (exit {process.returncode}); see {folder / 'process.log'}")
        results[route] = {"exit_code": process.returncode, **validate(media, duration, args.expect)}
        print(f"PASS: {route}: real CPU transcription, TXT and SRT", flush=True)
    report = {"model": "small.en", "device": "cpu", "compute_type": "int8",
              "duration_seconds": duration, "results": results}
    (run / "results.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    print(f"Local evidence: {run}")


if __name__ == "__main__":
    main()
