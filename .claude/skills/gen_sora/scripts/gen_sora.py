import argparse
import os
import time
from pathlib import Path

from openai import OpenAI


def _load_env() -> None:
    """Load environment variables from a .env file if python-dotenv is available."""
    try:
        from dotenv import find_dotenv, load_dotenv
    except Exception:
        return

    dotenv_path = find_dotenv(usecwd=True)
    if dotenv_path:
        load_dotenv(dotenv_path, override=False)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a Sora video from a prompt and save it to a file path."
    )
    parser.add_argument(
        "prompt",
        help="Text prompt used to generate the video.",
    )
    parser.add_argument(
        "output_path",
        help="Where to save the resulting MP4 file (e.g. ./out/video.mp4).",
    )
    parser.add_argument(
        "--model",
        default=os.getenv("SORA_MODEL", "sora-2"),
        help="Sora model deployment name (default: env SORA_MODEL or 'sora-2').",
    )
    parser.add_argument(
        "--seconds",
        type=int,
        default=8,
        help="Optional video duration in seconds (default: 8).",
    )
    parser.add_argument(
        "--size",
        default="1280x720",
        help="Optional video resolution in WIDTHxHEIGHT format (default: 1280x720).",
    )
    parser.add_argument(
        "--poll-seconds",
        type=int,
        default=int(os.getenv("SORA_POLL_SECONDS", "20")),
        help="Polling interval in seconds (default: env SORA_POLL_SECONDS or 20).",
    )
    parser.add_argument(
        "--input-reference",
        default=None,
        help=(
            "Optional input_reference to pass to the videos.create request "
            "(default: empty). If omitted, the parameter is not sent."
        ),
    )
    return parser.parse_args()


def _create_client() -> OpenAI:
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    base_url = os.getenv("AZURE_OPENAI_BASE_URL")
    if not api_key:
        raise SystemExit(
            "Missing env AZURE_OPENAI_API_KEY. Set it before running this script."
        )
    if not base_url:
        raise SystemExit(
            "Missing env AZURE_OPENAI_BASE_URL (e.g. https://<resource>.openai.azure.com/openai/v1/)."
        )
    print(f"[DEBUG] Using base_url: {base_url}")
    return OpenAI(api_key=api_key, base_url=base_url)


def main() -> None:
    _load_env()
    args = _parse_args()
    output_path = Path(args.output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    client = _create_client()

    # Create the video (don't use create_and_poll)
    create_kwargs = {
        "model": args.model,
        "prompt": args.prompt,
        "seconds": str(args.seconds),
        "size": args.size,
    }

    # Open input_reference file if provided
    input_file = None
    if args.input_reference:
        input_file = open(args.input_reference, "rb")
        create_kwargs["input_reference"] = input_file

    try:
        video = client.videos.create(**create_kwargs)
    finally:
        if input_file:
            input_file.close()

    print(f"Video creation started. ID: {video.id}")
    print(f"Initial status: {video.status}")

    # Poll
    while video.status not in ["completed", "failed", "cancelled"]:
        print(f"Status: {video.status}. Waiting {args.poll_seconds} seconds...")
        time.sleep(args.poll_seconds)
        video = client.videos.retrieve(video.id)

    if video.status != "completed":
        raise SystemExit(f"Video creation ended with status: {video.status}\n{video}")

    content = client.videos.download_content(video.id, variant="video")
    content.write_to_file(str(output_path))
    print(f"Saved {output_path}")


if __name__ == "__main__":
    main()





