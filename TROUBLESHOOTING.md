# Troubleshooting

## Python cannot be found

Install 64-bit Python 3.12 from [python.org](https://www.python.org/downloads/windows/), enable the option to add Python to PATH, and reopen the launcher. Supported versions are 3.10 through 3.12. The launchers try `py` first and then `python`; a missing runtime for one `py` version is not itself a fatal error.

If `winget` is unavailable or installation is blocked, install Python manually. Managed computers may require your administrator's help.

## First run is slow or the model download fails

Initial setup installs packages, and the selected model downloads on its first use. Check the terminal for download progress and leave it open. Confirm internet access and free disk space. A proxy, firewall, certificate problem, or restricted Hugging Face access can prevent model downloads. Retry after connectivity is restored; completed downloads are cached.

No paid API or authentication token is required for the default public models. An offline first run needs packages and model files provisioned in advance.

## Missing or incompatible packages

Run these commands inside the affected project folder:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip check
```

If `.venv` is incomplete and has no pip, run `python -m venv .venv` first to repair it. You do not need to delete recordings, transcripts, or an otherwise working environment.

The projects use `faster-whisper==1.2.1` and `av>=11,<19`. Keep the PyAV upper bound: this engine version uses a decoding argument removed in PyAV 19. The English launcher can repair an installed PyAV 19+ version. The bilingual launcher verifies packages and installs its requirements when needed. The bilingual tool also needs `opencc-python-reimplemented` for Traditional Chinese conversion.

## The window closes, a script is blocked, or a file cannot be found

Drag a single file onto the English BAT. For the bilingual version, drag a file or double-click a transcription BAT to open the file picker. Launch from a terminal if you need to retain the error output.

The BAT files invoke Windows PowerShell with an execution-policy bypass for that process. Organization policy can still block execution; follow your administrator's policy. Command-line examples in the README use the same process-local option.

Quote paths containing spaces. Non-ASCII paths are supported; the English script safely escapes characters that a legacy redirected console cannot display. This affects console messages only; output files remain UTF-8. Run under a user account that can read the media and write to its containing folder.

## Audio decoding fails or no speech appears

Try playing the recording normally. An extension does not guarantee that a file contains a supported, undamaged audio stream. A video with no audio track, silent recording, unsupported codec, or corrupt file cannot produce a useful transcript. Export a short WAV copy and try that copy if necessary.

Voice activity detection skips silence and may miss very faint speech. Empty TXT/SRT files mean that no non-empty speech segments were returned; process exit status alone does not establish that speech was recognized. Listen to the input and inspect the outputs.

## Transcription is slow, inaccurate, or uses the wrong language

Both scripts explicitly use CPU inference with int8 computation. Long recordings and larger models can take substantial time. The English CLI accepts `tiny.en` and `base.en` for speed; the bilingual standard launcher uses `small`, while the higher accuracy launcher uses `medium`.

Use the English version for English-only recordings. The bilingual launcher assumes Chinese-dominant mixed speech. For a different balance, use the bilingual Python CLI's `--language auto` or `--language en`. A prompt supplies context rather than strict instructions, and mixed-language transcription still needs review.

The bilingual tool preserves English speech and converts recognized Chinese characters; it does not generate a translation track.

## Outputs are missing, incomplete, or replaced

Look beside the original media for `_transcript.txt` and `_subtitles.srt`. Both scripts write results incrementally, so an interrupted or failed job can leave partial outputs. Rerunning overwrites those same output names. Back up any outputs you want to retain before rerunning.

The English BAT now preserves the transcription process's failure status. Read the error as well as the generated files. The original bilingual BAT files are preserved; automated callers should invoke its PowerShell launcher or Python script directly to obtain a reliable error status.

## Media or transcripts appear in Git

Run `git status --short` before staging. The repository ignores recordings, SRT/VTT files, TXT transcripts, model files, environments, and caches. Do not use `git add -f` on local recordings or secrets. Ignore rules cannot protect a file that was already committed; stop before pushing and inspect its history if that happens.
