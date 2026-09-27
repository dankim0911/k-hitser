import argparse
import subprocess
import sys
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(
        description="Generate songs.json, then build the printable card PDF."
    )
    parser.add_argument(
        "playback_csv",
        nargs="?",
        type=Path,
        default=BASE_DIR / "songs.csv",
        help="CSV with Artist, Title, Year, VideoId, Start, and End columns",
    )
    parser.add_argument(
        "--cards-csv",
        type=Path,
        default=BASE_DIR / "songs.csv",
        help="card data CSV (default: songs.csv beside this script)",
    )
    args = parser.parse_args()

    commands = (
        [
            sys.executable,
            str(BASE_DIR / "generate_songs.py"),
            str(args.playback_csv.resolve()),
            str(BASE_DIR / "songs.json"),
        ],
        [
            sys.executable,
            str(BASE_DIR / "generate_cards.py"),
            str(args.cards_csv.resolve()),
        ],
    )

    try:
        for command in commands:
            subprocess.run(command, cwd=BASE_DIR, check=True)
    except subprocess.CalledProcessError as error:
        raise SystemExit(error.returncode) from error


if __name__ == "__main__":
    main()