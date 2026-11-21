#!/usr/bin/env python3
"""News Image - Friday 20 November 2026.

A pure-Python (standard library only) newspaper poster that sums up the
world news of Friday 20 November 2026 in one 1024x1024 PNG image.

The program draws everything itself: it defines its own 5x7 bitmap font
and its own PNG encoder (zlib + struct), so it needs no Pillow, no
matplotlib, no network and no external font files.

Running ``python3 main.py`` writes ``entry.png`` to $MAKEFUN_OUTPUT_DIR
when that variable is set, otherwise to /output/entry.png. Output is
deterministic: two runs produce byte-identical files.
"""

import os
import struct
import zlib

WIDTH = 1024
HEIGHT = 1024

# ---------------------------------------------------------------------------
# Colours
# ---------------------------------------------------------------------------
PAPER = (250, 246, 239)   # warm off-white
INK = (26, 26, 26)        # near-black
NAVY = (31, 58, 95)       # headline blue
RED = (160, 32, 32)       # masthead red / number blocks
GREY = (110, 108, 100)    # rules and secondary text
LIGHT_RULE = (205, 198, 186)
GOLD = (176, 124, 30)     # icon accents

# ---------------------------------------------------------------------------
# 5x7 bitmap font, defined from scratch in this file.
# Each glyph is 7 rows of 5 characters ('#' = pixel on, '.' = off).
# ---------------------------------------------------------------------------
FONT = {
    "A": (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "##..#", "##..#", "#.#.#", "#..##", "#..##", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    "X": ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "a": (".....", ".....", ".###.", "....#", ".####", "#...#", ".###."),
    "b": ("#....", "#....", "####.", "#...#", "#...#", "#...#", "####."),
    "c": (".....", ".....", ".####", "#....", "#....", "#....", ".####"),
    "d": ("....#", "....#", ".####", "#...#", "#...#", "#...#", ".###."),
    "e": (".....", ".....", ".###.", "#...#", "#####", "#....", ".###."),
    "f": ("..##.", ".#..#", ".#...", "####.", ".#...", ".#...", ".#..."),
    "g": (".....", ".....", ".###.", "#...#", "#...#", ".###.", "#...."),
    "h": ("#....", "#....", "####.", "#...#", "#...#", "#...#", "#...#"),
    "i": (".....", "..#..", ".....", ".##..", "..#..", "..#..", ".###."),
    "j": (".....", "...#.", ".....", "..##.", "...#.", "...#.", "...#.", "##..."),
    "k": ("#....", "#....", "#..#.", "#.#..", "##...", "#.#..", "#..#."),
    "l": (".##..", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "m": (".....", ".....", "##.#.", "#.#.#", "#.#.#", "#.#.#", "#.#.#"),
    "n": (".....", ".....", "####.", "#...#", "#...#", "#...#", "#...#"),
    "o": (".....", ".....", ".###.", "#...#", "#...#", "#...#", ".###."),
    "p": (".....", ".....", "####.", "#...#", "#...#", "####.", "#...."),
    "q": (".....", ".....", ".####", "#...#", "#...#", ".####", "....#"),
    "r": (".....", ".....", "#.##.", "##..#", "#....", "#....", "#...."),
    "s": (".....", ".....", ".####", "#....", ".###.", "....#", "####."),
    "t": (".#...", ".#...", "####.", ".#...", ".#...", ".#..#", "..##."),
    "u": (".....", ".....", "#...#", "#...#", "#...#", "#..##", ".##.#"),
    "v": (".....", ".....", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "w": (".....", ".....", "#...#", "#.#.#", "#.#.#", "#.#.#", ".#.#."),
    "x": (".....", ".....", "#...#", ".#.#.", "..#..", ".#.#.", "#...#"),
    "y": (".....", ".....", "#...#", "#...#", ".#.#.", "..#..", "..#.."),
    "z": (".....", ".....", "#####", "....#", "...#.", "..#..", "#####"),
    "0": (".###.", "#..##", "#.#.#", "##..#", "#...#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "2": (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    "3": ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "...#.", "..#..", "..#..", "..#.."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ",": (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    ":": (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ";": (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "?": (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    '"': (".#.#.", ".#.#.", ".#.#.", ".....", ".....", ".....", "....."),
    "-": (".....", ".....", ".....", ".###.", ".....", ".....", "....."),
    "(": ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
    ")": (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
    "/": ("....#", "...#.", "...#.", "..#..", ".#...", ".#...", "#...."),
    "%": ("#...#", "#..#.", "...#.", "..#..", ".#...", ".#..#", "#...#"),
    "+": (".....", "..#..", "..#..", ".###.", "..#..", "..#..", "....."),
    "=": (".....", ".....", ".###.", ".....", ".###.", ".....", "....."),
    "&": (".##..", "#..#.", "#..#.", ".#...", "#.#.#", "#..#.", ".##.#"),
    "*": (".....", ".#.#.", "..#..", "#####", "..#..", ".#.#.", "....."),
    "#": (".#.#.", ".#.#.", "#####", ".#.#.", "#####", ".#.#.", ".#.#."),
    "@": (".###.", "#...#", "#.###", "#.#.#", "#.###", "#....", ".###."),
    "_": (".....", ".....", ".....", ".....", ".....", ".....", "#####"),
    "<": ("...#.", "..#..", ".#...", "#....", ".#...", "..#..", "...#."),
    ">": (".#...", "..#..", "...#.", "....#", "...#.", "..#..", ".#..."),
    "[": (".###.", ".#...", ".#...", ".#...", ".#...", ".#...", ".###."),
    "]": (".###.", "...#.", "...#.", "...#.", "...#.", "...#.", ".###."),
}

# Fix the "j" glyph: it must have exactly 7 rows like every other glyph.
FONT["j"] = (".....", "...#.", ".....", "..##.", "...#.", "...#.", "...#.")


# ---------------------------------------------------------------------------
# Canvas and drawing primitives
# ---------------------------------------------------------------------------
class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(w * h * 3)
        self.fill_rect(0, 0, w, h, bg)

    def set_px(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = color

    def fill_rect(self, x, y, w, h, color):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        r, g, b = color
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.px[i], self.px[i + 1], self.px[i + 2] = r, g, b

    def hline(self, x, y, w, color, thick=1):
        self.fill_rect(x, y, w, thick, color)

    def vline(self, x, y, h, color, thick=1):
        self.fill_rect(x, y, thick, h, color)

    def line(self, x0, y0, x1, y1, color, thick=1):
        """Bresenham line, with optional thickness."""
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.fill_rect(x0 - thick // 2, y0 - thick // 2, thick, thick, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, color, filled=False):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                d2 = (xx - cx) ** 2 + (yy - cy) ** 2
                if filled:
                    if d2 <= r * r:
                        self.set_px(xx, yy, color)
                else:
                    if abs(d2 - r * r) <= r * 2:
                        self.set_px(xx, yy, color)


# ---------------------------------------------------------------------------
# Text rendering with the 5x7 font
# ---------------------------------------------------------------------------
def glyph(ch):
    return FONT.get(ch, FONT["?"])


def text_width(text, scale):
    if not text:
        return 0
    return len(text) * 6 * scale - scale


def draw_text(cv, x, y, text, scale, color, align="left"):
    w = text_width(text, scale)
    if align == "center":
        x -= w // 2
    elif align == "right":
        x -= w
    cx = x
    for ch in text:
        rows = glyph(ch)
        for ry, row in enumerate(rows):
            for rx, bit in enumerate(row):
                if bit == "#":
                    cv.fill_rect(cx + rx * scale, y + ry * scale, scale, scale, color)
        cx += 6 * scale
    return w


def wrap_text(text, scale, max_w):
    lines = []
    cur = ""
    for word in text.split(" "):
        trial = (cur + " " + word).strip()
        if text_width(trial, scale) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


# ---------------------------------------------------------------------------
# The eight stories of Friday 20 November 2026
# ---------------------------------------------------------------------------
STORIES = [
    {
        "headline": "RUSSIA LAUNCHES MASSIVE AIR ATTACK",
        "support": "110+ missiles, 400+ drones overnight; 3 Kyiv bridges hit, at least 8 killed, power cut.",
        "icon": "missile",
    },
    {
        "headline": "CYCLONE AKVAN HITS ODISHA",
        "support": "Landfall near Gopalpur, winds 70-80 km/h; 300,000+ evacuated, no deaths reported at first.",
        "icon": "cyclone",
    },
    {
        "headline": "TANKER ABLAZE IN HORMUZ STRAIT",
        "support": "Projectile strike 8 nautical miles north of Khasab; Iran's Guards claim it hit a mine.",
        "icon": "ship",
    },
    {
        "headline": "SAUDIS INTERCEPT HOUTHI MISSILE",
        "support": "Kingdom downs a ballistic missile and 5 drones, strikes Hodeidah - a day after PIF Tower was hit.",
        "icon": "shield",
    },
    {
        "headline": "EU AND UK RESET RELATIONS",
        "support": "Brussels summit agrees food, carbon and youth-mobility deals - 100,000 places each way. Von der Leyen calls it a \"turning point\".",
        "icon": "flags",
    },
    {
        "headline": "KERCH BRIDGE RAIL LINK REOPENS",
        "support": "Trains resume on one track at slow speed; road span stays closed, no repair date yet.",
        "icon": "bridge",
    },
    {
        "headline": "GLOBAL STOCKS SLIDE ON AI FEARS",
        "support": "Nikkei down 5%, S&P 500 falls a sixth straight session; Asia's worst week since 2020.",
        "icon": "chart",
    },
    {
        "headline": "EU SENDS EUR 1 BILLION MORE AID",
        "support": "Military aid for Ukraine - drones, air defence, ammunition - by end-2027; EUR 7.9 billion also disbursed.",
        "icon": "coin",
    },
]


# ---------------------------------------------------------------------------
# Small drawn pictograms (one per story), 56x56 box at (x, y)
# ---------------------------------------------------------------------------
def draw_icon(cv, kind, x, y):
    cx, cy = x + 28, y + 28
    if kind == "missile":
        # rocket body + burst
        cv.line(cx - 6, cy + 16, cx + 6, cy - 14, NAVY, 4)
        cv.line(cx + 6, cy - 14, cx + 12, cy - 4, NAVY, 3)
        cv.line(cx + 6, cy - 14, cx + 0, cy - 4, NAVY, 3)
        cv.circle(cx + 8, cy - 18, 4, RED, filled=True)
        cv.line(cx - 14, cy + 20, cx - 20, cy + 26, GOLD, 3)
        cv.line(cx - 6, cy + 22, cx - 8, cy + 28, GOLD, 3)
        cv.line(cx + 2, cy + 20, cx + 6, cy + 27, GOLD, 3)
    elif kind == "cyclone":
        # spiral: three offset arcs
        cv.circle(cx, cy, 20, NAVY)
        cv.circle(cx + 4, cy + 2, 13, NAVY)
        cv.circle(cx - 2, cy - 2, 7, RED, filled=True)
        cv.line(cx - 24, cy + 18, cx - 12, cy + 24, GOLD, 3)
        cv.line(cx + 12, cy - 22, cx + 22, cy - 16, GOLD, 3)
    elif kind == "ship":
        # hull + flame
        cv.line(cx - 20, cy + 6, cx + 20, cy + 6, NAVY, 4)
        cv.line(cx - 20, cy + 6, cx - 14, cy + 18, NAVY, 3)
        cv.line(cx + 20, cy + 6, cx + 14, cy + 18, NAVY, 3)
        cv.line(cx - 14, cy + 18, cx + 14, cy + 18, NAVY, 3)
        cv.vline(cx - 4, cy - 12, 18, NAVY, 3)
        cv.vline(cx + 8, cy - 8, 14, NAVY, 3)
        cv.line(cx - 4, cy - 12, cx - 12, cy - 2, RED, 3)
        cv.line(cx - 4, cy - 12, cx + 4, cy - 2, GOLD, 3)
        cv.line(cx - 4, cy - 12, cx - 4, cy + 2, RED, 3)
    elif kind == "shield":
        # shield outline + check
        cv.line(cx - 16, cy - 18, cx + 16, cy - 18, NAVY, 3)
        cv.line(cx - 16, cy - 18, cx - 16, cy + 4, NAVY, 3)
        cv.line(cx + 16, cy - 18, cx + 16, cy + 4, NAVY, 3)
        cv.line(cx - 16, cy + 4, cx, cy + 20, NAVY, 3)
        cv.line(cx + 16, cy + 4, cx, cy + 20, NAVY, 3)
        cv.line(cx - 9, cy - 1, cx - 2, cy + 7, RED, 4)
        cv.line(cx - 2, cy + 7, cx + 11, cy - 9, RED, 4)
    elif kind == "flags":
        # two crossed flag poles with stars
        cv.line(cx - 12, cy - 20, cx - 12, cy + 20, NAVY, 3)
        cv.line(cx + 12, cy - 20, cx + 12, cy + 20, NAVY, 3)
        cv.fill_rect(cx - 12, cy - 20, 24, 12, NAVY)
        cv.fill_rect(cx + 12, cy - 20, 24, 12, RED)
        cv.circle(cx, cy - 14, 2, GOLD, filled=True)
        cv.circle(cx + 24, cy - 14, 2, GOLD, filled=True)
        cv.line(cx - 20, cy + 24, cx + 20, cy + 24, GOLD, 3)
    elif kind == "bridge":
        # arc + deck + pillars
        cv.line(cx - 24, cy + 12, cx + 24, cy + 12, NAVY, 4)
        cv.line(cx - 24, cy + 12, cx - 24, cy - 6, NAVY, 3)
        cv.line(cx + 24, cy + 12, cx + 24, cy - 6, NAVY, 3)
        cv.line(cx - 24, cy - 6, cx, cy - 20, NAVY, 3)
        cv.line(cx, cy - 20, cx + 24, cy - 6, NAVY, 3)
        cv.vline(cx - 12, cy - 12, 24, NAVY, 2)
        cv.vline(cx, cy - 18, 30, NAVY, 2)
        cv.vline(cx + 12, cy - 12, 24, NAVY, 2)
        cv.circle(cx, cy - 20, 3, RED, filled=True)
    elif kind == "chart":
        # axes + falling line with arrowhead
        cv.vline(cx - 20, cy - 20, 42, NAVY, 3)
        cv.hline(cx - 20, cy + 22, 44, NAVY, 3)
        cv.line(cx - 16, cy - 14, cx - 4, cy - 6, RED, 4)
        cv.line(cx - 4, cy - 6, cx + 6, cy + 2, RED, 4)
        cv.line(cx + 6, cy + 2, cx + 18, cy + 14, RED, 4)
        cv.line(cx + 18, cy + 14, cx + 10, cy + 14, RED, 3)
        cv.line(cx + 18, cy + 14, cx + 18, cy + 6, RED, 3)
    elif kind == "coin":
        # coin with star
        cv.circle(cx, cy, 20, GOLD, filled=True)
        cv.circle(cx, cy, 20, NAVY)
        cv.circle(cx, cy, 14, NAVY)
        cv.line(cx, cy - 9, cx + 3, cy - 2, NAVY, 3)
        cv.line(cx + 3, cy - 2, cx + 10, cy - 2, NAVY, 3)
        cv.line(cx + 10, cy - 2, cx + 5, cy + 3, NAVY, 3)
        cv.line(cx + 5, cy + 3, cx + 7, cy + 10, NAVY, 3)
        cv.line(cx + 7, cy + 10, cx, cy + 6, NAVY, 3)
        cv.line(cx, cy + 6, cx - 7, cy + 10, NAVY, 3)
        cv.line(cx - 7, cy + 10, cx - 5, cy + 3, NAVY, 3)
        cv.line(cx - 5, cy + 3, cx - 10, cy - 2, NAVY, 3)
        cv.line(cx - 10, cy - 2, cx - 3, cy - 2, NAVY, 3)
        cv.line(cx - 3, cy - 2, cx, cy - 9, NAVY, 3)


# ---------------------------------------------------------------------------
# PNG encoder (stdlib only): raw scanlines, filter 0, zlib level 9
# ---------------------------------------------------------------------------
def write_png(path, cv):
    raw = bytearray()
    stride = cv.w * 3
    for y in range(cv.h):
        raw.append(0)  # filter type 0 (none)
        raw += cv.px[y * stride:(y + 1) * stride]
    compressed = zlib.compress(bytes(raw), 9)

    def chunk(typ, data):
        out = struct.pack(">I", len(data)) + typ + data
        out += struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)
        return out

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", compressed)
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)


# ---------------------------------------------------------------------------
# Poster layout
# ---------------------------------------------------------------------------
def draw_poster():
    cv = Canvas(WIDTH, HEIGHT, PAPER)

    # --- Masthead ---------------------------------------------------------
    draw_text(cv, WIDTH // 2, 30, "THE WORLD IN ONE IMAGE", 3, GREY, align="center")
    # The date: large, dominant, exact wording.
    draw_text(cv, WIDTH // 2, 76, "Friday 20 November 2026", 6, RED, align="center")
    draw_text(
        cv, WIDTH // 2, 138,
        "Eight stories that defined the day - from Kyiv to the Gulf",
        2, GREY, align="center",
    )
    cv.hline(32, 170, WIDTH - 64, RED, 4)
    cv.hline(32, 178, WIDTH - 64, INK, 2)

    # --- Story grid: 2 columns x 4 rows ----------------------------------
    col_x = [32, 530]
    col_w = 462
    row_y0 = 196
    row_h = 200

    for i, story in enumerate(STORIES):
        col = i % 2
        row = i // 2
        bx = col_x[col]
        by = row_y0 + row * row_h

        cv.hline(bx, by, col_w, LIGHT_RULE, 2)

        # Number block
        cv.fill_rect(bx, by + 14, 34, 34, RED)
        draw_text(cv, bx + 17, by + 20, str(i + 1), 3, PAPER, align="center")

        # Pictogram, top right
        draw_icon(cv, story["icon"], bx + col_w - 58, by + 8)

        # Headline (bold navy, up to 2 lines)
        head_lines = wrap_text(story["headline"], 3, col_w - 46 - 66)
        hy = by + 12
        for line in head_lines[:2]:
            draw_text(cv, bx + 46, hy, line, 3, NAVY)
            hy += 26

        # Supporting line (up to 4 lines)
        sup_lines = wrap_text(story["support"], 2, col_w)
        sy = by + 84
        for line in sup_lines[:4]:
            draw_text(cv, bx, sy, line, 2, INK)
            sy += 20

    # --- Footer -----------------------------------------------------------
    cv.hline(32, 994, WIDTH - 64, LIGHT_RULE, 2)
    draw_text(
        cv, WIDTH // 2, 1004,
        "Compiled from CNN, Reuters, AP, IMD, The Hindu, Consilium and more.",
        2, GREY, align="center",
    )
    return cv


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "entry.png")
    cv = draw_poster()
    write_png(out_path, cv)
    print("Wrote", out_path, "(%dx%d)" % (WIDTH, HEIGHT))


if __name__ == "__main__":
    main()
