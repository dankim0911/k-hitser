import argparse
import csv
import json
from pathlib import Path
from urllib.parse import parse_qs, urlparse


BASE_DIR = Path(__file__).resolve().parent
REQUIRED_COLUMNS = {"Artist", "Title", "Year", "VideoId", "Start", "End"}


def extract_video_id(value):
    value = value.strip()
    parsed = urlparse(value)

    if parsed.scheme or parsed.netloc:
        if parsed.netloc.lower() in {"youtu.be", "www.youtu.be"}:
            return parsed.path.strip("/").split("/")[0]
        if parsed.netloc.lower().endswith("youtube.com"):
            if parsed.path == "/watch":
                return parse_qs(parsed.query).get("v", [""])[0]
            parts = parsed.path.strip("/").split("/")
            if len(parts) >= 2 and parts[0] in {"embed", "shorts", "live"}:
                return parts[1]
        raise ValueError(f"Unsupported YouTube URL: {value}")

    return value


def load_songs(csv_path):
    songs = []

    with csv_path.open("r", encoding="utf-8-sig", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        columns = set(reader.fieldnames or [])
        missing = REQUIRED_COLUMNS - columns
        if missing:
            raise ValueError(f"CSV is missing required columns: {', '.join(sorted(missing))}")

        for row_number, row in enumerate(reader, start=2):
            try:
                artist = row["Artist"].strip()
                title = row["Title"].strip()
                video_id = extract_video_id(row["VideoId"])
                year = int(row["Year"])
                start = int(row["Start"])
                end = int(row["End"])

                if not artist or not title or not video_id:
                    raise ValueError("Artist, Title, and VideoId must not be empty")
                if start < 0 or end <= start:
                    raise ValueError("End must be greater than Start, and Start cannot be negative")
            except (AttributeError, TypeError, ValueError) as error:
                raise ValueError(f"Invalid data on CSV row {row_number}: {error}") from error

            songs.append({
                "id": len(songs) + 1,
                "title": title,
                "artist": artist,
                "year": year,
                "videoId": video_id,
                "start": start,
                "end": end,
            })

    return songs


def main():
    parser = argparse.ArgumentParser(description="Generate songs.json from the song CSV.")
    parser.add_argument(
        "csv_file", nargs="?", type=Path, default=BASE_DIR / "khitser-songs.csv",
        help="source CSV (default: khitser-songs.csv beside this script)",
    )
    parser.add_argument(
        "json_file", nargs="?", type=Path, default=BASE_DIR / "songs.json",
        help="output JSON (default: songs.json beside this script)",
    )
    args = parser.parse_args()

    try:
        songs = load_songs(args.csv_file)
        with args.json_file.open("w", encoding="utf-8", newline="\n") as json_file:
            json.dump(songs, json_file, ensure_ascii=False, indent=2)
            json_file.write("\n")
    except (OSError, ValueError) as error:
        parser.error(str(error))

    print(f"Wrote {len(songs)} songs to {args.json_file}")


if __name__ == "__main__":
    main()