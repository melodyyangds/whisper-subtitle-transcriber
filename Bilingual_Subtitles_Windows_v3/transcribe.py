"""Local M4A/MP3/MP4 transcription: Mandarin-English -> Traditional Chinese SRT/TXT.

Requirements: faster-whisper==1.2.1, av>=11,<19, opencc-python-reimplemented
Works on CPU; the model is downloaded once and cached locally.
"""
import argparse
from pathlib import Path

from faster_whisper import WhisperModel


SUPPORTED_EXTENSIONS = {
    ".m4a", ".mp3", ".wav", ".mp4", ".mov", ".mkv",
    ".flac", ".ogg", ".webm", ".aac", ".wma",
}

# Whisper uses initial_prompt as contextual text, not a hard instruction.
# These examples prime mixed Chinese/English vocabulary without asking it to translate.
MIXED_LANGUAGE_PROMPT = (
    "這是一段以繁體中文為主、偶爾穿插英文的對話。"
    "例如：我們可以看一下這個 project 的 data，再確認最後的 result。"
)


def srt_time(seconds: float) -> str:
    millis = round(seconds * 1000)
    hour, rest = divmod(millis, 3_600_000)
    minute, rest = divmod(rest, 60_000)
    second, ms = divmod(rest, 1000)
    return f"{hour:02}:{minute:02}:{second:02},{ms:03}"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Transcribe Chinese/English M4A, MP3, or video to TXT and SRT on CPU."
    )
    parser.add_argument("media", type=Path, help="Path to an audio/video file")
    parser.add_argument(
        "--model", choices=("tiny", "base", "small", "medium", "large-v3"),
        default="small", help="Default: small; medium is usually more accurate but slower on CPU",
    )
    parser.add_argument(
        "--language", choices=("zh", "en", "auto"), default="zh",
        help="Dominant language; zh is best for mostly Chinese audio (default: zh)",
    )
    parser.add_argument(
        "--chinese", choices=("traditional", "simplified"), default="traditional",
        help="Convert Chinese subtitles to Traditional Chinese (default) or keep model output",
    )
    parser.add_argument(
        "--prompt", default=MIXED_LANGUAGE_PROMPT,
        help="Optional vocabulary/context hint for mixed-language transcription",
    )
    args = parser.parse_args()
    media = args.media.expanduser().resolve()
    if not media.is_file():
        parser.error(f"File not found: {media}")
    if media.suffix.lower() not in SUPPORTED_EXTENSIONS:
        print(f"Note: unusual extension {media.suffix!r}; will still attempt audio decoding.", flush=True)

    converter = None
    if args.chinese == "traditional":
        try:
            from opencc import OpenCC
            converter = OpenCC("s2tw")  # Traditional Chinese, Taiwan variant
        except ImportError:
            parser.error(
                "Missing OpenCC. Run the .bat launcher to install it automatically, "
                "or install: pip install opencc-python-reimplemented"
            )

    print(f"Loading multilingual Whisper '{args.model}' on CPU (int8)...", flush=True)
    print("The model is downloaded only the first time it is used.", flush=True)
    model = WhisperModel(args.model, device="cpu", compute_type="int8")
    segments, info = model.transcribe(
        str(media),
        task="transcribe",  # Preserve spoken language, do not translate into English.
        language=None if args.language == "auto" else args.language,
        multilingual=True,  # Re-detect language by segment; helps full English passages.
        condition_on_previous_text=False,  # Prevent language-switch carry-over and mistranslation.
        initial_prompt=args.prompt,
        beam_size=5,
        vad_filter=True,
    )
    txt_path = media.with_name(media.stem + "_transcript.txt")
    srt_path = media.with_name(media.stem + "_subtitles.srt")
    print(f"Transcribing: {media.name} ({info.duration / 60:.1f} minutes)", flush=True)
    print(f"Dominant language setting: {args.language}; detected: {info.language}", flush=True)

    count = 0
    # UTF-8 with BOM is recognized by modern Windows Notepad and many subtitle players.
    # Write segment by segment to preserve progress on lengthy CPU jobs.
    with txt_path.open("w", encoding="utf-8-sig") as text_out, srt_path.open("w", encoding="utf-8-sig") as srt_out:
        for segment in segments:
            line = segment.text.strip()
            if not line:
                continue
            if converter is not None:
                line = converter.convert(line)
            count += 1
            text_out.write(line + "\n")
            srt_out.write(
                f"{count}\n{srt_time(segment.start)} --> {srt_time(segment.end)}\n{line}\n\n"
            )
            text_out.flush()
            srt_out.flush()
            if count % 25 == 0:
                print(f"Processed through {segment.end / 60:.1f} min...", flush=True)

    if count == 0:
        print("No speech segments were recognized. Check audio content and format.", flush=True)
    print(f"Finished. Segments: {count}", flush=True)
    print(f"TXT: {txt_path}", flush=True)
    print(f"SRT: {srt_path}", flush=True)


if __name__ == "__main__":
    main()
