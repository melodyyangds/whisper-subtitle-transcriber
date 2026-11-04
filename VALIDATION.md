# Publication validation

Validated on Windows on November 4, 2026, with Python 3.12.10 and Windows PowerShell 5.1.

## English: real transcription

The English Python script, PowerShell launcher, and BAT launcher each successfully transcribed an 11-second English speech recording using the default `small.en` model, `device="cpu"`, and `compute_type="int8"`.

The sample was the public [JFK fixture from Whisper's test suite](https://github.com/openai/whisper/blob/main/tests/jfk.flac). Its SHA-256 was `63a4b1e4c1dc655ac70961ffbf518acd249df237e5a0152faae9a4a836949715`. The sample, generated transcripts, and logs are excluded from Git.

| Entry point | Exit status | Non-empty TXT | Valid SRT timestamps | TXT matches SRT | Expected speech |
| --- | --- | --- | --- | --- | --- |
| Python | 0 | Passed | Passed | Passed | Passed |
| Windows PowerShell | 0 | Passed | Passed | Passed | Passed |
| Windows BAT | 0 | Passed | Passed | Passed | Passed |

Validation checked contiguous cue numbers, timestamp syntax, start/end order, times within the recording's duration, matching TXT/SRT text, and recognition of the words `ask` and `country`. Cue segmentation varied between runs; identical segmentation is not required. Paths included spaces and a non-ASCII repository directory.

Reproduce using the English environment:

```powershell
.\English_Video_Transcriber_Windows\.venv\Scripts\python.exe tests\live_smoke.py "D:\Media\Short English sample.flac" --expect "ask" --expect "country"
```

Use expected words that actually occur in your own sample. This command performs real inference and retains local results under ignored `.validation/`.

## English fixes

Each production change followed a reproduced failure and regression test:

- Blank speech segments no longer create gaps in SRT cue numbers.
- `Transcribe_Video.bat` preserves the transcription failure status after its pause.
- Console logging handles Unicode file paths under a legacy redirected Windows encoding without crashing. Generated transcription files remain UTF-8.

The English PowerShell implementation was preserved. Its missing-file handling and dependency check were exercised in native Windows PowerShell, and its successful path was exercised by the live test.

## Bilingual preservation

All eight original top-level bilingual project files match their pre-publication SHA-256 hashes byte for byte, including the Python script, all BAT/PowerShell launchers, requirements, dependency checker, and original Chinese guide.

The existing environment passed:

- `verify_install.py`, including actual OpenCC conversion to Traditional Chinese.
- The PowerShell launcher's `-SetupOnly` check, which reused the healthy environment.
- `pip check`.
- Automated regression checks for mixed-language output, blank segments, CPU settings, timestamp boundaries, missing inputs, and empty results.

The owner had already successfully tested this version on Windows. No new live Mandarin/English accuracy test was performed for publication, and that earlier user test is not presented as a new automated live result. The working implementation was preserved.

## Automated checks

```powershell
python -m unittest discover -s tests -v
```

All 13 tests passed with no skips on the publication Windows machine:

- Two Git ignore-policy tests.
- Seven Python regression tests covering both tools.
- Four native Windows launcher tests, including missing arguments/files, BAT failure status, and the PowerShell dependency-check path.

All seven project/test Python files compiled successfully, both PowerShell scripts passed syntax parsing, and both virtual environments passed `pip check`.

The English environment used `faster-whisper 1.2.1`, `av 18.1.0`, `ctranslate2 4.8.5`, `onnxruntime 1.31.1`, and `huggingface-hub 2.4.0`. Requirements pin the engine and constrain PyAV; transitive dependencies are not fully locked.

## Scope and limitations

The live test establishes that short English audio can complete through all three entry points on this Windows machine. It is not a broad accuracy benchmark, a test of every media codec, or a performance guarantee for long recordings. A GPU and paid APIs were not used.

Package/model downloads require internet access before an offline run. The automatically installed Python/winget path was not exercised because Python was already installed. The bilingual BAT wrappers retain their original behavior; automated callers should use its PowerShell or Python entry point for reliable failure status.
