# Whisper Subtitle Transcriber

Local audio and video transcription for Windows, with an English edition and a Mandarin–English edition. Turn recordings into plain-text transcripts and timed SRT subtitles using CPU inference, without a GPU or paid transcription API.

[Windows setup and usage](docs/USAGE.md) · [繁體中文](README.zh-TW.md) · [Troubleshooting](TROUBLESHOOTING.md) · [Technical overview](docs/ARCHITECTURE.md) · [Validation results](VALIDATION.md)

## What it does

- Transcribes a local audio or video file into UTF-8 TXT and SRT files.
- Offers drag-and-drop Windows BAT launchers and Python command-line access.
- Runs Whisper locally through [faster-whisper](https://github.com/SYSTRAN/faster-whisper), using CPU int8 computation.
- Supports English-only recordings and Chinese-dominant conversations that include English.
- Converts recognized Chinese text to Traditional Chinese in the bilingual edition.
- Writes results incrementally, preserving completed segments if a long job is interrupted.

Suitable inputs include interviews, lectures, meeting recordings, and other speech recordings you have permission to process. Speech recognition is imperfect; review the results before sharing or publishing them.

## Choose an edition

| | English | Mandarin–English |
| --- | --- | --- |
| Project folder | `English_Video_Transcriber_Windows` | `Bilingual_Subtitles_Windows_v3` |
| Best suited to | English recordings | Chinese-dominant recordings with English words or passages |
| Default model | `small.en` | Multilingual `small` |
| Standard launcher | `Transcribe_Video.bat` | `Transcribe_Audio_Video.bat` |
| File selection | Drag a file onto the BAT | Drag a file onto the BAT, or double-click to choose one |
| Larger model option | Select a model through Python | `Transcribe_Higher_Accuracy.bat` uses `medium` |

The bilingual edition preserves spoken English and converts recognized Chinese characters to Traditional Chinese. It produces one transcript and one subtitle track, rather than parallel translations.

## Get started on Windows

**You need:** 64-bit Python 3.10–3.12, Windows PowerShell 5.1, and internet access for initial package and model downloads. Python 3.12 is the tested version. A separate FFmpeg executable is not needed for the common formats decoded by PyAV.

1. [Download the ZIP](https://github.com/melodyyangds/whisper-subtitle-transcriber/archive/refs/heads/main.zip) and extract it fully. Git users can instead clone the repository:

   ```powershell
   git clone https://github.com/melodyyangds/whisper-subtitle-transcriber.git
   cd whisper-subtitle-transcriber
   ```

2. Open the edition's folder in File Explorer.
3. Drag a short recording onto its standard BAT launcher. The bilingual BAT also supports a file picker when double-clicked.
4. On the first run, wait for environment setup and the model download. Keep the window open until it reports completion.
5. Look beside the original recording for `_transcript.txt` and `_subtitles.srt` files.

Each edition creates its own `.venv` environment. The launchers attempt a Python 3.12 installation through `winget` if a supported Python cannot be found; installing Python yourself first is more predictable. You do not need to activate a virtual environment for the BAT workflow.

See the [full Windows guide](docs/USAGE.md) for manual setup, command-line options, subtitle playback, and offline use.

## Example output

For an input file named `sample_audio.wav`, the tool saves a transcript and subtitles in the same folder:

```text
sample_audio.wav
sample_audio_transcript.txt
sample_audio_subtitles.srt
```

An illustrative SRT cue looks like this; it is a format example, not a measured recognition result:

```srt
1
00:00:00,000 --> 00:00:02,500
This is a short audio sample.
```

Both files use UTF-8; bilingual output also includes a byte order mark for Windows compatibility. Re-running the same input overwrites its generated TXT and SRT files. Copy earlier outputs elsewhere if you want to retain them.

## Validation

The English edition completed real CPU transcription of an 11-second public English speech sample through **Python, Windows PowerShell, and BAT**. All three runs produced non-empty TXT and SRT outputs with matching text, valid timestamps, and expected speech.

The project also has **13 automated regression tests** covering timestamp boundaries, file writing, empty and blank segments, input validation, CPU settings, mixed-language preservation, console encoding, launcher failure handling, and Git ignore rules.

The bilingual implementation was already tested successfully by the owner on Windows. Its eight original files were preserved byte for byte during publication; dependency verification and regression checks passed. A new live Mandarin–English accuracy test was not performed for publication.

Read the [validation record](VALIDATION.md) for exact test scope, environment versions, sample provenance, and limitations. These results are not an accuracy benchmark across languages or a performance guarantee for long recordings.

## How it works

```text
BAT launcher → PowerShell setup → Python transcription
                                  ├─ PyAV: decode local media
                                  ├─ faster-whisper: CPU speech recognition
                                  ├─ OpenCC: Traditional Chinese conversion (bilingual)
                                  └─ TXT and SRT: write beside the input
```

The implementation emphasizes a practical Windows workflow: isolated dependencies, explicit CPU settings, readable scripts, incremental output, and tests for platform-specific failures. See the [technical overview](docs/ARCHITECTURE.md) for design decisions, repository structure, and development commands.

## Privacy and limitations

Transcription runs on your machine. The scripts do not send recordings to a transcription API. Initial setup contacts package and model hosts; after the necessary packages and model files are cached, inference can run offline.

No recordings, generated transcripts, downloaded models, virtual environments, or credentials are included in this repository. Git ignore rules help keep those files out of future commits.

The launchers process one file at a time. Codec support depends on the recording's contents, and voice activity detection may miss very quiet speech. Larger models require more memory and time on a CPU. Automatic captions need human review, especially for names and language switches.

## Help and feedback

Start with [troubleshooting](TROUBLESHOOTING.md). If you find a reproducible problem, [open an issue](https://github.com/melodyyangds/whisper-subtitle-transcriber/issues) with your Windows and Python versions, chosen edition and model, and the error message. Remove personal paths and private transcript text before sharing logs; do not attach sensitive recordings.

## Acknowledgments

Speech recognition is provided by [Whisper](https://github.com/openai/whisper), [faster-whisper](https://github.com/SYSTRAN/faster-whisper), and [CTranslate2](https://github.com/OpenNMT/CTranslate2). Media decoding uses [PyAV](https://github.com/PyAV-Org/PyAV); Chinese character conversion uses [OpenCC](https://github.com/yichen0831/opencc-python).
