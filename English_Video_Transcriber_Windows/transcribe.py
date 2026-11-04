"""Offline CPU transcription after one-time model download."""
import argparse
from pathlib import Path
import sys

from faster_whisper import WhisperModel


def srt_time(seconds):
    milliseconds = round(seconds * 1000)
    h, remainder = divmod(milliseconds, 3_600_000)
    m, remainder = divmod(remainder, 60_000)
    s, ms = divmod(remainder, 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"


def main():
    # Redirected Windows consoles may use a legacy encoding that cannot display
    # Unicode filenames. Keep transcription files UTF-8 and console logging safe.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="backslashreplace")
    parser = argparse.ArgumentParser()
    parser.add_argument("media", type=Path)
    parser.add_argument("--model", default="small.en", help="Whisper model, default small.en")
    args = parser.parse_args()
    media = args.media.resolve()
    if not media.is_file():
        parser.error(f"File not found: {media}")

    print("Loading model (first run downloads it; CPU mode, no NVIDIA required)...", flush=True)
    model = WhisperModel(args.model, device="cpu", compute_type="int8")
    segments, info = model.transcribe(
        str(media), language="en", beam_size=5, vad_filter=True
    )
    txt = media.with_name(media.stem + "_transcript.txt")
    srt = media.with_name(media.stem + "_subtitles.srt")
    print(f"Transcribing: {media.name} — detected duration {info.duration / 60:.1f} minutes", flush=True)
    count = 0
    # Write incremental results so a lengthy CPU run is not lost if interrupted.
    with txt.open("w", encoding="utf-8") as text_out, srt.open("w", encoding="utf-8") as sub_out:
        for segment in segments:
            line = segment.text.strip()
            if not line:
                continue
            count += 1
            text_out.write(line + "\n")
            sub_out.write(f"{count}\n{srt_time(segment.start)} --> {srt_time(segment.end)}\n{line}\n\n")
            text_out.flush()
            sub_out.flush()
            if count % 25 == 0:
                print(f"Processed through {segment.end / 60:.1f} min...", flush=True)
    print(f"Saved: {txt}\nSaved: {srt}", flush=True)


if __name__ == "__main__":
    main()
