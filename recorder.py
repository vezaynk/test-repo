#!/usr/bin/env python3
"""Twitch stream recorder — polls a channel and records when live."""

import argparse
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path


def is_live(channel: str) -> bool:
    """Return True if the channel is currently streaming."""
    result = subprocess.run(
        ["streamlink", "--quiet", f"https://www.twitch.tv/{channel}", "best", "--url"],
        capture_output=True,
        text=True,
    )
    return result.returncode == 0


def record(channel: str, output_dir: Path, quality: str) -> Path:
    """Record the stream until it ends. Returns the output file path."""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_file = output_dir / f"{channel}_{timestamp}.ts"
    print(f"[*] Recording to {output_file}")
    subprocess.run(
        [
            "streamlink",
            f"https://www.twitch.tv/{channel}",
            quality,
            "-o",
            str(output_file),
        ]
    )
    return output_file


def main() -> None:
    parser = argparse.ArgumentParser(description="Record Twitch streams automatically.")
    parser.add_argument("channel", help="Twitch channel name")
    parser.add_argument(
        "-o",
        "--output-dir",
        default=".",
        help="Directory to save recordings (default: current directory)",
    )
    parser.add_argument(
        "-q",
        "--quality",
        default="best",
        help="Stream quality: best, 1080p, 720p, 480p, worst (default: best)",
    )
    parser.add_argument(
        "-i",
        "--interval",
        type=int,
        default=30,
        help="Seconds between live-check polls when offline (default: 30)",
    )
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"[*] Watching {args.channel} — checking every {args.interval}s")

    try:
        while True:
            if is_live(args.channel):
                print(f"[+] {args.channel} is live — starting recording")
                recording = record(args.channel, output_dir, args.quality)
                print(f"[+] Stream ended. Saved to {recording}")
            else:
                print(f"[-] {args.channel} is offline — retrying in {args.interval}s")
                time.sleep(args.interval)
    except KeyboardInterrupt:
        print("\n[*] Stopped by user.")
        sys.exit(0)


if __name__ == "__main__":
    main()
