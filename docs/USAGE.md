# Windows setup and usage

[Project overview](../README.md) · [繁體中文快速入門](../README.zh-TW.md) · [Troubleshooting](../TROUBLESHOOTING.md)

## 1. Prepare your computer

Use Windows with **64-bit Python 3.10, 3.11, or 3.12** and **Windows PowerShell 5.1**. Python 3.12 is the validated version. Install Python from [python.org](https://www.python.org/downloads/windows/) if needed, select **Add python.exe to PATH**, and reopen your terminal after installation.

Check the interpreter in PowerShell:

```powershell
python --version
```

Use a supported version rather than assuming that the newest Python release will work with the pinned engine. Package installation and model downloads need internet access. Disk and memory requirements depend on the model; start with the standard launcher and a short recording.

## 2. Download the project

On the [repository page](https://github.com/melodyyangds/whisper-subtitle-transcriber), select **Code → Download ZIP**, then extract the archive. Run the tools from the extracted folder, rather than from inside the ZIP preview. You do not need Git for this method.

Alternatively, use Git:

```powershell
git clone https://github.com/melodyyangds/whisper-subtitle-transcriber.git
cd whisper-subtitle-transcriber
```

Keep the Python script, PowerShell script, and BAT launcher together inside each edition's folder. Downloading only a BAT file is insufficient.

## 3. Run your first transcription

### English audio or video

1. Open `English_Video_Transcriber_Windows` in File Explorer.
2. Drag **one file** onto `Transcribe_Video.bat`.
3. Leave the window open while it sets up the environment and downloads `small.en` on first use.
4. Wait for the completion message and output paths, then press a key to close the window.

Opening the English BAT without a file displays drag-and-drop instructions. It does not open a file picker.

### Mandarin–English audio or video

1. Open `Bilingual_Subtitles_Windows_v3`.
2. Double-click `Transcribe_Audio_Video.bat` and choose a file, or drag one file onto it.
3. Wait for setup and transcription to finish.

The standard launcher uses the multilingual `small` model. `Transcribe_Higher_Accuracy.bat` uses `medium`, a larger model that generally trades CPU speed and memory for recognition quality. Improvement is not guaranteed for every recording.

`First_Time_Setup_Optional.bat` prepares the bilingual environment without transcribing a file. Its existing [Traditional Chinese release guide](../Bilingual_Subtitles_Windows_v3/README_使用說明_繁體中文.txt) is retained for reference; current validation is documented [separately](../VALIDATION.md).

### What happens on the first run?

The launcher finds a supported Python, creates a project-local `.venv`, and installs free transcription packages. If Python is absent, it attempts to install Python 3.12 using `winget`. Install Python manually if that is blocked or unavailable.

The selected Whisper model downloads the first time it is loaded and is cached by the model library. Subsequent runs reuse cached models and installed packages. A model download or long CPU job may take time without producing subtitle files immediately. Leave the console open and check its status messages.

You do not need an API key, GPU, virtual-environment activation command, or paid transcription account.

## 4. Find and use the results

For `lecture.m4a`, the outputs appear **in the same folder as the recording**:

```text
lecture_transcript.txt
lecture_subtitles.srt
```

- Open the TXT in an editor such as Notepad to read or revise the transcript.
- Open the SRT in an editor to inspect its text and timestamps, or load it as an external subtitle track in a compatible video player.
- For players that discover subtitles by filename, make a copy named to match the video, such as `lecture.srt` beside `lecture.mp4`, or select the SRT manually.

Original media is left unchanged. Repeating a run replaces the generated files with the same names. An interrupted job can leave partial files because segments are written incrementally. Back up earlier outputs before rerunning.

Outputs are UTF-8; bilingual output includes a UTF-8 byte order mark. Names, punctuation, numbers, quiet speech, and language switches may need correction.

## Command-line usage

The commands in this section run from the **repository root** unless a `cd` step says otherwise. Replace `D:\Media\...` with a real path on your machine and keep quotes around paths containing spaces.

### PowerShell launchers: automatic setup

```powershell
# English, using small.en
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\English_Video_Transcriber_Windows\transcribe.ps1 -MediaPath "D:\Media\English interview.mp4"

# Bilingual, standard model
powershell.exe -NoProfile -STA -ExecutionPolicy Bypass -File .\Bilingual_Subtitles_Windows_v3\transcribe.ps1 -MediaPath "D:\Media\Meeting.m4a" -Model small

# Bilingual, larger model
powershell.exe -NoProfile -STA -ExecutionPolicy Bypass -File .\Bilingual_Subtitles_Windows_v3\transcribe.ps1 -MediaPath "D:\Media\Meeting.m4a" -Model medium

# Bilingual, setup only
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\Bilingual_Subtitles_Windows_v3\transcribe.ps1 -SetupOnly
```

The bilingual PowerShell launcher accepts `small` or `medium`. The English PowerShell launcher accepts a media path and uses `small.en`. Use Python below for other model choices and advanced language options.

### Manual English setup

From the repository root, enter the English project folder:

```powershell
cd English_Video_Transcriber_Windows
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe transcribe.py "D:\Media\English interview.mp4" --model small.en
```

For a smaller English model, replace `small.en` with `tiny.en` or `base.en`. Smaller models prioritize speed and resource usage and may be less accurate. The Python CLI also accepts a compatible model name or local model path supported by faster-whisper; models beyond the default were not exhaustively validated here.

### Manual bilingual setup

From the repository root, enter the bilingual project folder:

```powershell
cd Bilingual_Subtitles_Windows_v3
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe verify_install.py
.\.venv\Scripts\python.exe transcribe.py "D:\Media\Meeting.m4a" --model small --language zh --chinese traditional
```

Available bilingual Python options:

| Option | Accepted values | Default | Purpose |
| --- | --- | --- | --- |
| `--model` | `tiny`, `base`, `small`, `medium`, `large-v3` | `small` | Select the multilingual Whisper model |
| `--language` | `zh`, `en`, `auto` | `zh` | Set the dominant language or enable automatic detection |
| `--chinese` | `traditional`, `simplified` | `traditional` | Convert Chinese to Taiwan Traditional Chinese, or leave model text unconverted |
| `--prompt` | A quoted context string | Built-in Mandarin–English vocabulary hint | Supply topic or vocabulary context |

The `simplified` value leaves model output unchanged; it does not guarantee exclusively Simplified Chinese characters. The prompt provides recognition context rather than enforcing a translation or exact spelling.

For automatic language detection, from inside the bilingual folder:

```powershell
.\.venv\Scripts\python.exe transcribe.py "D:\Media\Mixed conversation.wav" --language auto
```

For a technical vocabulary hint:

```powershell
.\.venv\Scripts\python.exe transcribe.py "D:\Media\Project discussion.wav" --language zh --prompt "Project context: Python, SQL, data pipeline, dashboard."
```

You can view each Python CLI's options without running inference:

```powershell
.\.venv\Scripts\python.exe transcribe.py --help
```

## Supported inputs and offline use

Common input extensions include `.mp4`, `.m4a`, `.mp3`, `.wav`, `.mov`, `.mkv`, `.flac`, `.ogg`, `.webm`, `.aac`, and `.wma`. The underlying codec must be decodable and the file must contain an audio stream. A corrupt recording or silent clip cannot produce a useful transcript. No separate FFmpeg executable is required for the common formats decoded by PyAV.

After packages and a chosen model have been downloaded, transcription can run offline. A different model still needs its own first download. The scripts process recordings locally and do not call a paid speech API.

The tool handles one input per run and does not implement batch folders, speaker diarization, a desktop GUI, or parallel translation tracks. See [troubleshooting](../TROUBLESHOOTING.md) for decoding errors, missing packages, slow runs, and empty outputs.
