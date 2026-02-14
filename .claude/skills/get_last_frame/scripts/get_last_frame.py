from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path
from typing import Optional

try:  # Optional dependency; use if available
    import cv2  # type: ignore
except ImportError:  # noqa: F401
    cv2 = None  # type: ignore


def _extract_with_ffmpeg(src: Path, dst: Path) -> None:
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise RuntimeError("ffmpeg not found in PATH; install ffmpeg or install opencv-python for fallback")

    # Use sseof to seek from end and grab the last decoded frame
    cmd = [
        ffmpeg,
        "-y",
        "-sseof",
        "-1",
        "-i",
        str(src),
        "-frames:v",
        "1",
        str(dst),
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def _extract_with_cv2(src: Path, dst: Path) -> None:
    if cv2 is None:
        raise RuntimeError("opencv-python is not installed")

    cap = cv2.VideoCapture(str(src))
    if not cap.isOpened():
        raise RuntimeError(f"Failed to open video: {src}")

    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if frame_count <= 0:
        cap.release()
        raise RuntimeError("Video has no frames")

    # Set to last frame index
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_count - 1)
    ok, frame = cap.read()
    cap.release()
    if not ok or frame is None:
        raise RuntimeError("Unable to read last frame")

    if not cv2.imwrite(str(dst), frame):
        raise RuntimeError(f"Failed to write image: {dst}")


def extract_last_frame(src: Path, dst: Path) -> None:
    if not src.exists():
        raise FileNotFoundError(f"Input video not found: {src}")
    dst.parent.mkdir(parents=True, exist_ok=True)

    # Prefer ffmpeg because it's faster and avoids extra deps
    try:
        _extract_with_ffmpeg(src, dst)
        return
    except Exception as ffmpeg_err:  # noqa: B902
        # Try cv2 fallback
        if cv2 is None:
            raise ffmpeg_err
        _extract_with_cv2(src, dst)


def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Save the final frame of an MP4 to an image file")
    parser.add_argument("input", help="Path to input mp4")
    parser.add_argument("output", help="Path to output image (png/jpg)")
    return parser.parse_args(argv)


def main(argv: Optional[list[str]] = None) -> int:
    args = parse_args(argv)
    src = Path(args.input)
    dst = Path(args.output)
    extract_last_frame(src, dst)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
