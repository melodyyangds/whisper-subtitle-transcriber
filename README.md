# Whisper Subtitle Transcriber

Two Windows tools for turning local audio and video into readable transcripts and timed subtitles. Both run Whisper locally on the CPU using [faster-whisper](https://github.com/SYSTRAN/faster-whisper). No GPU, API key, subscription, or paid transcription service is required.

Choose the English tool for English recordings, or the bilingual tool for Mandarin conversations that include English words and passages.

| | English | Bilingual |
| --- | --- | --- |
| Folder | `English_Video_Transcriber_Windows` | `Bilingual_Subtitles_Windows_v3` |
| Default model | `small.en` | Multilingual `small` |
| Language | English | Mandarin and English; Chinese-dominant by default |
| Chinese output | Not applicable | Traditional Chinese, Taiwan variant |
| Launcher | `Transcribe_Video.bat` | `Transcribe_Audio_Video.bat` |
| Higher accuracy option | Set a model through the Python CLI | `Transcribe_Higher_Accuracy.bat` uses `medium` |

The bilingual tool transcribes the spoken languages and converts Chinese characters to Traditional Chinese. It does not create parallel translations or translate all speech into one language.

## Requirements

- Windows with 64-bit Python 3.10–3.12; Python 3.12 is the tested version.
- Windows PowerShell 5.1, included with Windows.
- Internet access for the initial package installation and each model's first download.
- Enough memory and disk space for the selected model. Larger models use more resources and take longer on a CPU.

Launchers create a separate `.venv` inside each project. If a supported Python cannot be found, they attempt to install Python 3.12 with Windows Package Manager (`winget`). Installing Python yourself first makes setup more predictable.

Once packages and the selected model are cached, transcription can run offline. Media is processed locally. PyAV handles decoding; a separate FFmpeg executable is not required for the supported formats. See the [engine documentation](https://github.com/SYSTRAN/faster-whisper#requirements) for details.

## Quick start on Windows

Download and extract this repository, or clone it with Git:

```powershell
git clone https://github.com/melodyyangds/whisper-subtitle-transcriber.git
cd whisper-subtitle-transcriber
```

The repository is initially private, so cloning requires an authorized GitHub account.

### English recordings

1. Open `English_Video_Transcriber_Windows` in File Explorer.
2. Drag one English audio or video file onto `Transcribe_Video.bat`.
3. On the first run, wait for setup and the `small.en` model download.
4. Keep the window open until transcription finishes, then press a key to close it.

The English BAT expects a file dropped onto it. Opening it without a file displays instructions.

### Mandarin and English recordings

1. Open `Bilingual_Subtitles_Windows_v3`.
2. Double-click `Transcribe_Audio_Video.bat` to choose a file, or drag a file onto it.
3. Use `Transcribe_Higher_Accuracy.bat` for the larger, slower `medium` model.

`First_Time_Setup_Optional.bat` installs and verifies the bilingual environment without starting a transcription. The original [Traditional Chinese guide](Bilingual_Subtitles_Windows_v3/README_使用說明_繁體中文.txt) is also preserved. Its historical validation notes describe the original release; current checks are recorded in [VALIDATION.md](VALIDATION.md).

## Output files

For an input such as `meeting.mp4`, both tools write these files beside the original media:

```text
meeting_transcript.txt
meeting_subtitles.srt
```

The TXT contains recognized speech. The SRT contains numbered cues with timestamps such as `00:00:01,250 --> 00:00:03,000`. Files are UTF-8; bilingual output includes a UTF-8 byte order mark for Windows compatibility.

The tools do not modify the original recording. Running again on the same input overwrites the corresponding generated TXT and SRT files. Copy those outputs elsewhere first if you want to keep an earlier result. Speech recognition can make mistakes; review names, punctuation, language switches, and timing before publishing subtitles.

Common formats include MP4, M4A, MP3, WAV, MOV, MKV, FLAC, OGG, WEBM, AAC, and WMA. Actual decoding depends on the file's codec and contents. The launchers process one file per invocation.

## Command-line usage

Run commands from the repository root. Replace the example media path with your own file; quote paths containing spaces.

```powershell
# English: automatic setup, then transcription
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\English_Video_Transcriber_Windows\transcribe.ps1 -MediaPath "D:\Media\English interview.mp4"

# Bilingual: automatic setup, then transcription
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\Bilingual_Subtitles_Windows_v3\transcribe.ps1 -MediaPath "D:\Media\Meeting.m4a" -Model small
```

To install manually and choose an English model:

```powershell
cd English_Video_Transcriber_Windows
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe transcribe.py "D:\Media\English interview.mp4" --model small.en
```

Use `tiny.en` or `base.en` for a faster, less accurate English run. The English BAT and PowerShell launcher use `small.en`; use Python to select another model.

Bilingual manual setup and advanced options:

```powershell
cd Bilingual_Subtitles_Windows_v3
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe verify_install.py
.\.venv\Scripts\python.exe transcribe.py "D:\Media\Meeting.m4a" --model small --language zh --chinese traditional
```

The bilingual Python CLI accepts `--language zh`, `en`, or `auto`; `--chinese traditional` or `simplified`; and an optional `--prompt` for contextual vocabulary. The `simplified` option keeps Whisper's original character output without conversion, so it does not guarantee exclusively Simplified Chinese. Its model choices are `tiny`, `base`, `small`, `medium`, and `large-v3`.

## Tests and validation

Run the regression suite with any supported Python:

```powershell
python -m unittest discover -s tests -v
```

These tests exercise timestamp boundaries, output writing, blank segments, input validation, CPU settings, mixed language preservation, Windows console encoding, and native launcher failure handling. Unit tests replace model inference with a controlled test double; they do not measure recognition accuracy. Windows launcher tests run only on Windows. One dependency-check test requires the English `.venv`; install its requirements first to run all checks.

Run a separate live test with a short English recording you are comfortable using:

```powershell
.\English_Video_Transcriber_Windows\.venv\Scripts\python.exe tests\live_smoke.py "D:\Media\Short English sample.wav" --expect "a phrase spoken in the sample"
```

This performs real inference with `small.en` through Python, PowerShell, and BAT on Windows, checks both output files and SRT timing, and saves local evidence in ignored `.validation/`. It makes new test copies and leaves the supplied recording unchanged. The script uses the English virtual environment's Python so the direct and launcher runs share the same dependencies.

See [VALIDATION.md](VALIDATION.md) for the publication test results and [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for setup and decoding help.

## Repository contents and privacy

Both project folders retain their own source, launchers, and requirements. The bilingual implementation is preserved from the working local version. The English version includes small fixes for contiguous subtitle numbering, BAT failure reporting, and Unicode path logging.

`.gitignore` excludes media, generated transcripts and subtitles, virtual environments, model files, caches, credentials, and local validation artifacts. The original Chinese guide and dependency manifests are the only TXT files intentionally included. No recordings, generated transcripts, model weights, or API credentials are distributed with this repository. Ignore rules do not remove files already tracked by Git; review staged changes before every future upload.
