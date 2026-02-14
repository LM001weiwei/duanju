from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Iterable, List

try:  # Prefer bundled ffmpeg if available
    import imageio_ffmpeg  # type: ignore
except ImportError:  # noqa: F401
    imageio_ffmpeg = None  # type: ignore


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Concatenate multiple MP4 files in order into a single MP4 using ffmpeg (stream copy)."
    )
    parser.add_argument(
        "output",
        help="Destination MP4 path for the concatenated video (will be overwritten if it exists).",
    )
    parser.add_argument(
        "inputs",
        nargs="+",
        help="List of input MP4 files, in the order they should be concatenated (requires >= 2).",
    )
    return parser.parse_args()


def _validate_inputs(inputs: Iterable[str]) -> List[Path]:
    paths: List[Path] = []
    for raw in inputs:
        path = Path(raw).expanduser().resolve()
        if not path.exists():
            raise SystemExit(f"Input does not exist: {path}")
        if not path.is_file():
            raise SystemExit(f"Input is not a file: {path}")
        paths.append(path)
    if len(paths) < 2:
        raise SystemExit("Provide at least two input MP4 files to concatenate.")
    return paths


def _write_concat_file(paths: Iterable[Path]) -> Path:
    temp = tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8")
    try:
        for path in paths:
            escaped = path.as_posix().replace("'", "'\\''")
            temp.write(f"file '{escaped}'\n")
    finally:
        temp.close()
    return Path(temp.name)


def _run_ffmpeg(list_file: Path, output: Path) -> None:
    ffmpeg_bin = shutil.which("ffmpeg")
    if not ffmpeg_bin and imageio_ffmpeg is not None:
        ffmpeg_bin = imageio_ffmpeg.get_ffmpeg_exe()
    if not ffmpeg_bin:
        raise SystemExit(
            "ffmpeg not found. Install ffmpeg or install the imageio-ffmpeg package for a bundled binary."
        )

    cmd = [
        ffmpeg_bin,
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        str(list_file),
        "-c",
        "copy",
        str(output),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        sys.stderr.write(result.stderr)
        raise SystemExit(f"ffmpeg failed with exit code {result.returncode}")


def main() -> int:
    args = _parse_args()
    output_path = Path(args.output).expanduser().resolve()
    input_paths = _validate_inputs(args.inputs)

    list_file = _write_concat_file(input_paths)
    try:
        _run_ffmpeg(list_file, output_path)
    finally:
        list_file.unlink(missing_ok=True)

    print(f"Concatenated {len(input_paths)} files -> {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
