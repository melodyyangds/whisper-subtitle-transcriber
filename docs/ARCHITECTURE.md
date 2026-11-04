# Technical overview

[Project overview](../README.md) · [Usage guide](USAGE.md) · [Validation record](../VALIDATION.md)

## Project scope

This repository packages local speech recognition into a practical Windows workflow. The application work covers file handling, launcher setup, dependency isolation, recognition configuration, Chinese character conversion, and TXT/SRT output. The speech recognition models and inference engine are provided by the upstream projects listed below; this project does not train a new model.

The two editions remain separate so an English-only workflow stays simple while the bilingual edition can retain its working Mandarin–English behavior and conversion settings.

## Processing pipeline

1. A BAT wrapper accepts a dropped file. The bilingual wrappers can also invoke a file picker.
2. PowerShell finds Python, prepares an edition-specific `.venv`, and launches the Python script.
3. Python validates the input path and initializes `WhisperModel` with `device="cpu"` and `compute_type="int8"`.
4. faster-whisper decodes the recording through PyAV, applies voice activity detection, and returns speech segments with text and start/end times.
5. The bilingual script optionally converts recognized Chinese text using OpenCC's `s2tw` conversion.
6. The script skips blank segments and writes numbered SRT cues and transcript lines beside the original media, flushing after each segment.

The application does not upload media or depend on a paid transcription endpoint. Package and model downloads are separate first-run network operations.

## Recognition choices

| Choice | English edition | Bilingual edition |
| --- | --- | --- |
| Model default | `small.en` | `small` |
| Language | Fixed `en` | Default `zh`; Python CLI also supports `en` and `auto` |
| Search | Beam size 5 | Beam size 5 |
| Voice activity detection | Enabled | Enabled |
| Language switching | English-only workflow | `multilingual=True` and `condition_on_previous_text=False` |
| Context | No custom prompt exposed | Built-in mixed-language prompt; overridable through Python |
| Character conversion | None | Traditional Chinese by default |

These are configured application behaviors, rather than guarantees about recognition quality. A dominant-language setting, vocabulary prompt, or character converter cannot eliminate model errors.

## Repository map

```text
whisper-subtitle-transcriber/
├── English_Video_Transcriber_Windows/
│   ├── Transcribe_Video.bat
│   ├── transcribe.ps1
│   ├── transcribe.py
│   └── requirements.txt
├── Bilingual_Subtitles_Windows_v3/
│   ├── Transcribe_Audio_Video.bat
│   ├── Transcribe_Higher_Accuracy.bat
│   ├── First_Time_Setup_Optional.bat
│   ├── transcribe.ps1
│   ├── transcribe.py
│   ├── verify_install.py
│   ├── requirements.txt
│   └── README_使用說明_繁體中文.txt
├── tests/
│   ├── test_transcribers.py
│   ├── test_windows_launchers.py
│   ├── test_repository_hygiene.py
│   └── live_smoke.py
├── docs/
│   ├── USAGE.md
│   └── ARCHITECTURE.md
├── README.md
├── README.zh-TW.md
├── TROUBLESHOOTING.md
└── VALIDATION.md
```

## Dependencies and compatibility

Both editions pin `faster-whisper==1.2.1` and constrain PyAV to `av>=11,<19`. This avoids a decoding API incompatibility between this engine version and PyAV 19. The bilingual edition additionally requires `opencc-python-reimplemented`.

Separate environments prevent bilingual-only packages from becoming requirements for the English workflow. Transitive dependencies are not fully locked. Package versions from the Windows validation run are recorded in [VALIDATION.md](../VALIDATION.md).

## Run the tests

From the repository root:

```powershell
python -m unittest discover -s tests -v
```

The unit tests use a controlled replacement for slow model inference while exercising the real scripts' argument handling and file output. They cover timestamp rounding, blank and empty results, missing files, CPU/language settings, mixed-language output, and legacy console encoding.

Native Windows tests execute the actual BAT and PowerShell launchers. Install the English environment's requirements first to include the dependency-check test; without that environment, the test is skipped. Windows-only tests are skipped on other operating systems. Git ignore tests require a Git checkout and are skipped in a downloaded ZIP without `.git`.

Live inference is a separate, opt-in check using the English environment's Python:

```powershell
.\English_Video_Transcriber_Windows\.venv\Scripts\python.exe tests\live_smoke.py "D:\Media\Short English sample.wav" --expect "words present in the recording"
```

On Windows, this runs Python, PowerShell, and BAT independently. It checks exit status, non-empty outputs, contiguous cue numbering, SRT timestamp syntax and ordering, agreement between TXT and SRT text, and any expected phrases. Timestamp validation allows a one-second tolerance beyond the decoded duration. Test copies and evidence remain in ignored `.validation/`; the input recording is unchanged.

## Reliability boundaries

Incremental writes preserve completed segments, but a failed run may leave incomplete outputs. The scripts overwrite their generated filenames on a repeated run. Empty recognized speech can still produce empty files with a successful process exit, so consumers should inspect output content.

The English BAT preserves Python/PowerShell failure status. The original bilingual BAT wrappers were retained; automation should invoke its PowerShell or Python entry point directly for reliable failure status.

No automated confidence threshold, speaker diarization, batch orchestration, or exhaustive codec validation is implemented. The [validation record](../VALIDATION.md) distinguishes actual English live inference from controlled tests and the owner's earlier bilingual validation.
