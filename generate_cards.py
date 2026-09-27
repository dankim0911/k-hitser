import argparse
import csv
import os
from pathlib import Path

import qrcode
from qrcode.constants import ERROR_CORRECT_H
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader


BASE_DIR = Path(__file__).resolve().parent
CARD_URL = "https://dankim0911.github.io/k-hitser/?card={id}"
OUTPUT_FILE = BASE_DIR / "output" / "kpop_hitster_cards.pdf"

PAGE_WIDTH, PAGE_HEIGHT = letter
CARD_WIDTH = 2.5 * 72
CARD_HEIGHT = 2.625 * 72
COLUMNS = 3
ROWS = 4
CARDS_PER_PAGE = COLUMNS * ROWS
GAP_X = 0
GAP_Y = 0
LEFT_MARGIN = (PAGE_WIDTH - COLUMNS * CARD_WIDTH - (COLUMNS - 1) * GAP_X) / 2
TOP_MARGIN = (PAGE_HEIGHT - ROWS * CARD_HEIGHT - (ROWS - 1) * GAP_Y) / 2

INK = HexColor("#173B35")
ACCENT = HexColor("#D45E4C")
PAPER = HexColor("#FFFEFA")
GUIDE = HexColor("#AEB8B1")


def load_cards(csv_path):
    cards = []
    seen_ids = set()

    with csv_path.open("r", encoding="utf-8-sig", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        headers = {header.strip().lower(): header for header in (reader.fieldnames or [])}
        required = {"id", "title", "artist", "year"}
        missing = required - headers.keys()
        if missing:
            raise ValueError(f"CSV is missing required columns: {', '.join(sorted(missing))}")

        for row_number, row in enumerate(reader, start=2):
            values = {key: (row.get(header) or "").strip() for key, header in headers.items()}
            if not any(values.values()):
                continue

            try:
                card_id = int(values["id"])
                year = int(values["year"])
                title = values["title"]
                artist = values["artist"]
                if card_id < 1:
                    raise ValueError("ID must be a positive integer")
                if card_id in seen_ids:
                    raise ValueError(f"duplicate ID {card_id}")
                if not title or not artist:
                    raise ValueError("Title and artist must not be empty")
            except (KeyError, TypeError, ValueError) as error:
                raise ValueError(f"Invalid data on CSV row {row_number}: {error}") from error

            seen_ids.add(card_id)
            cards.append({"id": card_id, "title": title, "artist": artist, "year": year})

    if not cards:
        raise ValueError("The CSV contains no cards")
    return cards


def register_unicode_font(cards):
    text = " ".join(value for card in cards for value in (card["title"], card["artist"]))
    try:
        text.encode("cp1252")
        return "Helvetica", "Helvetica-Bold"
    except UnicodeEncodeError:
        pass

    windows_fonts = Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts"
    candidates = (
        windows_fonts / "malgun.ttf",
        windows_fonts / "arialuni.ttf",
        Path("/System/Library/Fonts/Supplemental/AppleGothic.ttf"),
        Path("/usr/share/fonts/truetype/nanum/NanumGothic.ttf"),
        Path("/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc"),
    )
    for font_path in candidates:
        if not font_path.is_file():
            continue
        try:
            pdfmetrics.registerFont(TTFont("CardUnicode", str(font_path), subfontIndex=0))
            return "CardUnicode", "CardUnicode"
        except Exception:
            continue

    raise ValueError(
        "The song data contains non-Western text, but no compatible Unicode font was found. "
        "Install Noto Sans CJK or Nanum Gothic, or add a supported font path to the script."
    )


def card_position(row, column):
    x = LEFT_MARGIN + column * (CARD_WIDTH + GAP_X)
    y = PAGE_HEIGHT - TOP_MARGIN - CARD_HEIGHT - row * (CARD_HEIGHT + GAP_Y)
    return x, y


def draw_card_frame(pdf, x, y):
    pdf.setFillColor(PAPER)
    pdf.setStrokeColor(GUIDE)
    pdf.setLineWidth(0.65)
    pdf.rect(x, y, CARD_WIDTH, CARD_HEIGHT, fill=1, stroke=1)


def make_qr(url):
    code = qrcode.QRCode(
        version=None,
        error_correction=ERROR_CORRECT_H,
        box_size=16,
        border=4,
    )
    code.add_data(url)
    code.make(fit=True)
    return ImageReader(code.make_image(fill_color="#173B35", back_color="#FFFFFF").convert("RGB"))


def draw_front(pdf, card, x, y):
    draw_card_frame(pdf, x, y)
    if card is None:
        return

    qr_size = 158.4
    qr_image = make_qr(CARD_URL.format(id=card["id"]))
    pdf.drawImage(
        qr_image,
        x + (CARD_WIDTH - qr_size) / 2,
        y + (CARD_HEIGHT - qr_size) / 2,
        width=qr_size,
        height=qr_size,
        preserveAspectRatio=True,
        mask="auto",
    )


def wrap_text(text, font_name, font_size, max_width):
    lines = []
    current = ""
    for word in text.split():
        candidate = f"{current} {word}".strip()
        if pdfmetrics.stringWidth(candidate, font_name, font_size) <= max_width:
            current = candidate
            continue
        if current:
            lines.append(current)
            current = ""
        if pdfmetrics.stringWidth(word, font_name, font_size) <= max_width:
            current = word
            continue
        for character in word:
            candidate = current + character
            if current and pdfmetrics.stringWidth(candidate, font_name, font_size) > max_width:
                lines.append(current)
                current = character
            else:
                current = candidate
    if current:
        lines.append(current)
    return lines or [""]


def draw_fitted_text(pdf, text, font_name, bold_font, max_size, min_size,
                     max_width, max_height, center_x, center_y):
    for size in range(max_size, min_size - 1, -1):
        lines = wrap_text(text, font_name, size, max_width)
        leading = size * 1.12
        if len(lines) * leading <= max_height:
            pdf.setFillColor(INK)
            pdf.setFont(bold_font, size)
            baseline = center_y + (len(lines) - 1) * leading / 2 - size * 0.35
            for line in lines:
                pdf.drawCentredString(center_x, baseline, line)
                baseline -= leading
            return
    raise ValueError(f"Text does not fit on card: {text}")


def draw_back(pdf, card, x, y, regular_font, bold_font):
    draw_card_frame(pdf, x, y)
    if card is None:
        return

    center_x = x + CARD_WIDTH / 2
    safe_width = CARD_WIDTH - 32
    draw_fitted_text(
        pdf, card["title"], regular_font, bold_font, 22, 11,
        safe_width, 60, center_x, y + 145,
    )
    draw_fitted_text(
        pdf, card["artist"], regular_font, bold_font, 15, 9,
        safe_width, 38, center_x, y + 82,
    )
    pdf.setFillColor(ACCENT)
    pdf.setStrokeColor(ACCENT)
    pdf.setLineWidth(1.5)
    pdf.line(center_x - 20, y + 51, center_x + 20, y + 51)
    pdf.setFillColor(INK)
    pdf.setFont(bold_font, 28)
    pdf.drawCentredString(center_x, y + 16, str(card["year"]))


def draw_sheet(pdf, cards, is_back, regular_font, bold_font):
    for index in range(CARDS_PER_PAGE):
        row, column = divmod(index, COLUMNS)
        card = cards[index] if index < len(cards) else None
        physical_column = COLUMNS - 1 - column if is_back else column
        x, y = card_position(row, physical_column)
        if is_back:
            draw_back(pdf, card, x, y, regular_font, bold_font)
        else:
            draw_front(pdf, card, x, y)
    pdf.showPage()


def generate_pdf(cards, output_path):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    regular_font, bold_font = register_unicode_font(cards)
    pdf = canvas.Canvas(str(output_path), pagesize=letter, pageCompression=1)
    pdf.setTitle("K-Pop Hitster Cards")
    pdf.setAuthor("K-Pop Hitster")

    for start in range(0, len(cards), CARDS_PER_PAGE):
        batch = cards[start:start + CARDS_PER_PAGE]
        draw_sheet(pdf, batch, False, regular_font, bold_font)
        draw_sheet(pdf, batch, True, regular_font, bold_font)

    pdf.save()


def main():
    parser = argparse.ArgumentParser(
        description="Generate duplex-ready K-Pop Hitster cards from a CSV file."
    )
    parser.add_argument(
        "csv_file", nargs="?", type=Path, default=BASE_DIR / "songs.csv",
        help="CSV with id,title,artist,year columns (default: songs.csv)",
    )
    parser.add_argument(
        "-o", "--output", type=Path, default=OUTPUT_FILE,
        help="output PDF path (default: output/kpop_hitster_cards.pdf)",
    )
    args = parser.parse_args()

    try:
        cards = load_cards(args.csv_file)
        generate_pdf(cards, args.output)
    except (OSError, ValueError) as error:
        parser.error(str(error))

    print(f"Wrote {len(cards)} cards to {args.output}")


if __name__ == "__main__":
    main()