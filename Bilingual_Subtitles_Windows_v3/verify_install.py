"""Dependency verification without fragile PowerShell 5.1 python -c quoting."""
import sys


def main():
    import av
    import opencc
    from faster_whisper import WhisperModel

    major = int(av.__version__.split(".")[0])
    if major >= 19:
        raise RuntimeError("PyAV 19+ is not supported by this package; run pip install -r requirements.txt")
    assert WhisperModel is not None
    assert opencc.OpenCC("s2tw").convert("简体中文") == "簡體中文"
    print("OK: faster-whisper, PyAV", av.__version__, "and OpenCC are ready.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"Verification failed: {type(exc).__name__}: {exc}", file=sys.stderr)
        sys.exit(1)
