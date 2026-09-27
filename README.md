# K-Pop Hitster

A homebrew Korean version of **HITSTER**. The website handles song playback; the physical cards carry a permanent numeric ID in a QR code and show the answer on the reverse.

## Generate Cards

Install Python 3.8 or newer and the PDF/QR dependencies:

```powershell
py -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

On macOS or Linux, use `python3 -m venv .venv`, then `.venv/bin/python -m pip install -r requirements.txt`.

Edit `songs.csv`, keeping one card per row:

```csv
id,title,artist,year
1,Gee,Girls' Generation,2009
2,Mister,KARA,2009
3,Fantastic Baby,BIGBANG,2012
```

IDs must be unique positive integers. Keep an ID unchanged if its song details or website playback information change. The generator ignores all fields except `id`, `title`, `artist`, and `year`; it does not modify `songs.json` or the website's video data.

Run the generator from the project directory:

```powershell
.venv\Scripts\python.exe generate_cards.py
```

This writes `output/kpop_hitster_cards.pdf`. A different CSV and output path can be supplied:

```text
python generate_cards.py path/to/songs.csv --output path/to/cards.pdf
```

To run both generators in sequence using `songs.csv` by default, run:

```powershell
.venv\Scripts\python.exe generate_all.py
```

The CSV includes `id`, `Artist`, `Title`, `Year`, `VideoId`, `Start`, and `End` columns. Both generators use it: `generate_songs.py` writes `songs.json`, then `generate_cards.py` writes the PDF. Keep IDs unique and unchanged. To use another source CSV, pass its path as the first argument; use `--cards-csv` to select a different card CSV.

The PDF uses US Letter pages, with each batch of up to twelve cards arranged as a front page followed by its matching answer-back page. QR codes encode the full `https://dankim0911.github.io/k-hitser/?card=<ID>` URL and include a print-sized quiet zone.

## Print and Cut

Print on US Letter paper at **Actual size / 100%**, double-sided, **flip on long edge** (portrait). Do not enable fit-to-page or shrink-to-printable-area scaling, since that changes the card dimensions. The back pages reverse the three columns to account for the long-edge flip; the text itself remains upright. Printer feed and duplex registration vary, so print one test sheet and check alignment before printing the full deck. Cut along the light card borders.

Cards are 2.5 × 2.625 inches, with square corners and no gaps between adjacent cards for straight-line cutting. The grid leaves 0.5-inch left/right margins and 0.25-inch top/bottom margins. If a printer clips the outer guides, use borderless printing or a print shop rather than scaling the PDF.

## Website

The web app is a static GitHub Pages site. To preview it locally, run `python -m http.server 8000` from the project directory and open `http://localhost:8000/?card=1`.

The website uses `songs.json` for video IDs and clip timestamps. To update it independently, run:

```text
python generate_songs.py
```
