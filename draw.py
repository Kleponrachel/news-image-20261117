#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Draw the news-image-20261117 entry: a dense newspaper front page summing up
Tuesday 17 November 2026 in world news - 43 real stories across 6 continents,
with a world map of the day's flashpoints. Rendered locally with Pillow;
the graded entrypoint is main.py, which only copies the PNG this script
renders. Output: entry.png, 1024x1024, under 1 MiB."""

import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = "/usr/share/fonts/truetype/dejavu"

SERIF_B = os.path.join(FONT_DIR, "DejaVuSerif-Bold.ttf")
SANS_B = os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")
SANS = os.path.join(FONT_DIR, "DejaVuSans.ttf")

W, H = 1024, 1024
PAPER = (248, 244, 236)
INK = (20, 20, 20)
GREY = (96, 96, 96)
RED = (179, 38, 30)
NAVY = (20, 33, 61)
RULE = (210, 203, 188)

MARGIN = 48
CW = W - 2 * MARGIN  # 928


def font(path, size):
    return ImageFont.truetype(path, size)


def fit_font(path, text, max_width, start_size):
    size = start_size
    while size > 10 and font(path, size).getlength(text) > max_width:
        size -= 1
    return font(path, size)


def wrap(text, fnt, max_width):
    lines, cur = [], ""
    for word in text.split(" "):
        trial = (cur + " " + word).strip()
        if fnt.getlength(trial) <= max_width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_spaced(draw, cx, y, text, fnt, fill, spacing=4):
    widths = [fnt.getlength(ch) for ch in text]
    total = sum(widths) + spacing * (len(text) - 1)
    x = cx - total / 2
    for ch, wch in zip(text, widths):
        draw.text((x, y), ch, font=fnt, fill=fill)
        x += wch + spacing


def draw_chip(draw, x, y, text, bg, fnt):
    tw = fnt.getlength(text)
    pad_x, pad_y = 9, 5
    w = int(tw + 2 * pad_x)
    h = fnt.size + 2 * pad_y
    draw.rounded_rectangle([x, y, x + w, y + h], radius=4, fill=bg)
    draw.text((x + pad_x, y + pad_y - 1), text, font=fnt, fill=(255, 255, 255))
    return w, h


# ---- simplified world map: continent outlines as (lon, lat) polygons ----
CONTINENTS = [
    # North America
    [(-168, 66), (-150, 70), (-130, 71), (-115, 69), (-100, 69), (-90, 68),
     (-85, 66), (-82, 62), (-76, 62), (-68, 58), (-60, 55), (-55, 52),
     (-60, 47), (-65, 44), (-70, 42), (-75, 37), (-76, 34), (-80, 30),
     (-81, 26), (-84, 30), (-90, 21), (-94, 17), (-97, 16), (-92, 15),
     (-87, 13), (-83, 10), (-80, 8), (-79, 9), (-85, 11), (-90, 14),
     (-95, 16), (-100, 18), (-105, 20), (-110, 23), (-115, 28), (-120, 34),
     (-124, 40), (-124, 48), (-130, 55), (-135, 58), (-145, 60), (-155, 58),
     (-162, 58)],
    # Greenland
    [(-45, 60), (-40, 64), (-32, 68), (-22, 70), (-25, 74), (-35, 77),
     (-50, 77), (-58, 74), (-55, 70), (-52, 64), (-48, 60)],
    # South America
    [(-79, 9), (-77, 6), (-77, 3), (-80, -3), (-81, -6), (-77, -12),
     (-72, -18), (-70, -23), (-70, -30), (-72, -37), (-73, -44), (-70, -50),
     (-66, -55), (-68, -52), (-65, -45), (-62, -40), (-58, -35), (-52, -32),
     (-48, -28), (-41, -23), (-39, -17), (-35, -9), (-35, -6), (-40, -3),
     (-44, -2), (-50, 0), (-52, 4), (-58, 7), (-62, 9), (-68, 11),
     (-72, 12), (-77, 8)],
    # Europe
    [(-10, 37), (-9, 43), (-2, 44), (-1, 46), (-4, 48), (-2, 49), (0, 51),
     (3, 53), (7, 54), (8, 57), (10, 59), (13, 56), (18, 56), (21, 55),
     (24, 58), (28, 59), (30, 60), (28, 64), (25, 68), (20, 70), (15, 68),
     (12, 64), (8, 62), (5, 60), (5, 58), (7, 55), (10, 54), (12, 51),
     (15, 48), (14, 45), (12, 44), (8, 44), (3, 43), (0, 40), (-2, 37),
     (-6, 36), (-9, 37)],
    # UK
    [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (0, 53)],
    # Africa
    [(-17, 15), (-16, 20), (-13, 27), (-10, 31), (-6, 33), (-1, 35),
     (5, 37), (10, 37), (15, 34), (20, 32), (25, 32), (30, 31), (32, 31),
     (34, 28), (36, 27), (38, 22), (40, 18), (43, 12), (48, 11), (51, 11),
     (50, 5), (48, 2), (44, -2), (40, -8), (38, -15), (35, -20), (33, -26),
     (32, -29), (28, -33), (24, -34), (20, -35), (17, -32), (15, -27),
     (13, -22), (12, -18), (12, -12), (13, -8), (12, -4), (9, -1), (9, 4),
     (4, 6), (-2, 5), (-8, 4), (-13, 8), (-15, 11)],
    # Asia
    [(28, 36), (30, 36), (33, 36), (36, 36), (38, 38), (42, 39), (44, 38),
     (48, 38), (50, 37), (53, 38), (54, 37), (57, 37), (58, 38), (55, 40),
     (52, 42), (50, 44), (52, 46), (55, 46), (58, 45), (60, 44), (63, 44),
     (66, 43), (70, 44), (73, 45), (75, 46), (78, 47), (80, 48), (82, 50),
     (85, 52), (88, 53), (90, 55), (95, 55), (100, 57), (105, 58), (110, 58),
     (115, 59), (120, 60), (125, 60), (130, 60), (135, 60), (140, 60),
     (142, 55), (142, 50), (140, 45), (138, 43), (135, 42), (132, 43),
     (130, 40), (128, 38), (126, 38), (124, 40), (122, 38), (120, 35),
     (118, 32), (115, 30), (112, 28), (110, 25), (108, 22), (106, 20),
     (105, 15), (104, 10), (102, 8), (100, 8), (99, 12), (98, 15), (96, 16),
     (94, 18), (92, 21), (90, 22), (88, 22), (86, 20), (83, 18), (80, 16),
     (78, 12), (76, 8), (75, 12), (73, 18), (72, 20), (70, 22), (68, 23),
     (66, 25), (63, 25), (60, 25), (58, 26), (56, 27), (54, 28), (52, 28),
     (50, 29), (48, 30), (46, 30), (44, 29), (42, 30), (40, 32), (38, 34),
     (36, 36)],
    # Australia
    [(114, -22), (113, -26), (115, -32), (116, -35), (120, -34), (124, -33),
     (129, -32), (132, -32), (135, -35), (138, -35), (140, -38), (144, -38),
     (147, -39), (150, -37), (153, -32), (153, -27), (151, -24), (149, -20),
     (146, -19), (143, -15), (142, -11), (140, -14), (137, -12), (135, -12),
     (132, -11), (129, -13), (126, -14), (123, -17), (120, -20), (117, -20)],
]

ISLANDS = [  # (lon, lat, rx, ry) small island groups
    (100, 0, 7, 3), (112, -3, 9, 3), (125, -2, 7, 3), (138, -4, 8, 3),
    (131, 34, 3, 6), (136, 37, 3, 6), (140, 40, 3, 6),
    (167, -41, 3, 6), (172, -43, 3, 5),
]

# (lon, lat) of the day's flashpoints
MARKERS = [(33.5, 45.3), (56, 26.8), (50.5, 26.0), (121, 14.6),
           (139.7, 35.7), (30, -1.9), (28.8, 47.0), (100.5, 13.7)]


def draw_map(draw, x0, y0, w, h):
    """Simplified world map (lon -180..180, lat 75..-55) with flashpoints."""
    draw.rectangle([x0, y0, x0 + w, y0 + h], fill=(226, 234, 240),
                   outline=RULE, width=1)

    def px(lon, lat):
        return (x0 + (lon + 180) / 360 * w,
                y0 + (75 - lat) / 130 * h)

    for poly in CONTINENTS:
        pts = [px(lon, lat) for lon, lat in poly]
        draw.polygon(pts, fill=(168, 190, 206), outline=(122, 151, 173))
    for lon, lat, rx, ry in ISLANDS:
        cx, cy = px(lon, lat)
        draw.ellipse([cx - rx, cy - ry, cx + rx, cy + ry],
                     fill=(168, 190, 206), outline=(122, 151, 173))
    for lon, lat in MARKERS:
        cx, cy = px(lon, lat)
        draw.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=(255, 255, 255))
        draw.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=RED)


def draw_lead2(draw, x, y, w, tag, color, headline, summary, hl_size=25,
               sm_size=17):
    """Secondary lead story: chip + headline + summary. Returns bottom y."""
    chip_f = font(SANS_B, 20)
    _, chh = draw_chip(draw, x, y, tag, color, chip_f)
    hl_f = font(SANS_B, hl_size)
    lines = wrap(headline, hl_f, w)
    assert len(lines) <= 2, "lead2 headline too long: " + headline
    ty = y + chh + 6
    for ln in lines:
        draw.text((x, ty), ln, font=hl_f, fill=INK)
        ty += hl_size + 5
    sm_f = font(SANS, sm_size)
    lines = wrap(summary, sm_f, w)
    assert len(lines) <= 2, "lead2 summary too long: " + summary
    ty += 2
    for ln in lines:
        draw.text((x, ty), ln, font=sm_f, fill=(60, 60, 60))
        ty += sm_size + 5
    return ty


def draw_column(draw, x, y, w, sections, hl_size=16):
    """One grid column: sections = [(header, color, [headlines])]."""
    hl_f = font(SANS_B, hl_size)
    hd_f = font(SANS_B, 16)
    ty = y
    for header, color, heads in sections:
        draw.rectangle([x, ty, x + w, ty + 22], fill=color)
        draw.text((x + 8, ty + 3), header, font=hd_f, fill=(255, 255, 255))
        ty += 22 + 5
        for hl in heads:
            lines = wrap(hl, hl_f, w)
            assert len(lines) <= 2, "brief too long: " + hl
            for ln in lines:
                draw.text((x, ty), ln, font=hl_f, fill=INK)
                ty += hl_size + 3
            ty += 3
        ty += 4
    return ty


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    d.rectangle([24, 24, W - 25, H - 25], outline=INK, width=3)

    # --- masthead ---
    draw_spaced(d, W // 2, 40, "THE DAY IN WORLD NEWS", font(SANS_B, 23),
                (122, 111, 90), spacing=5)
    date_f = fit_font(SERIF_B, "TUESDAY, 17 NOVEMBER 2026", CW, 58)
    d.text((W // 2, 66), "TUESDAY, 17 NOVEMBER 2026", font=date_f,
           fill=INK, anchor="ma")
    draw_spaced(d, W // 2, 122, "43 STORIES  \u2022  6 CONTINENTS  \u2022  ONE FRONT PAGE",
                font(SANS_B, 19), RED, spacing=2)
    d.rectangle([MARGIN, 146, W - MARGIN, 150], fill=RED)

    # --- top band: Kerch lead (left) + world map (right) ---
    ly = 158
    chip_f = font(SANS_B, 22)
    draw_chip(d, MARGIN, ly, "UKRAINE WAR", RED, chip_f)
    hl_f = font(SANS_B, 36)
    headline = "Ukraine drones cripple Kerch Bridge"
    lines = wrap(headline, hl_f, 512)
    assert len(lines) <= 2, "lead headline: " + str(lines)
    ty = ly + 44
    for ln in lines:
        d.text((MARGIN, ty), ln, font=hl_f, fill=INK)
        ty += 42
    sm_f = font(SANS, 19)
    summary = ("A span falls into the sea in the second strike in two days; "
               "two killed in Crimea. Russia hits Kyiv\u2019s bridges and "
               "metro in reply.")
    lines = wrap(summary, sm_f, 512)
    assert len(lines) <= 3, "lead summary: " + str(lines)
    ty += 2
    for ln in lines:
        d.text((MARGIN, ty), ln, font=sm_f, fill=(60, 60, 60))
        ty += 22
    assert ty <= 356, "lead text overflow: ends %d" % ty

    mx, my, mw = 580, ly, 396
    map_h = 160
    d.text((mx + mw // 2, my), "WORLD MAP \u2014 THE DAY\u2019S FLASHPOINTS",
           font=font(SANS_B, 15), fill=GREY, anchor="ma")
    draw_map(d, mx, my + 22, mw, map_h)
    d.text((mx + mw // 2, my + 22 + map_h + 6),
           "Kerch  \u2022  Qeshm  \u2022  Bahrain  \u2022  Manila  \u2022  Tokyo  \u2022  Kigali",
           font=font(SANS, 14), fill=GREY, anchor="ma")

    # --- second band: Qeshm + Markets ---
    sy = 368
    d.line([(MARGIN, sy - 8), (W - MARGIN, sy - 8)], fill=RULE, width=2)
    col_w = (CW - 24) // 2
    end1 = draw_lead2(
        d, MARGIN, sy, col_w, "GULF WAR", (14, 107, 122),
        "US jets hit Qeshm after Iran strikes US radar",
        "Iran hits a US radar base; US hits Qeshm.")
    end2 = draw_lead2(
        d, MARGIN + col_w + 24, sy, col_w, "MARKETS", (138, 109, 0),
        "Nasdaq enters correction as stocks slide",
        "Dow \u22121.4%, S&P 500 \u22121.9%, Nasdaq \u22122.5%.")
    grid_top = max(end1, end2) + 6
    assert grid_top <= 520, "second band too tall: %d" % grid_top

    # --- grid: 4 columns, 40 briefs ---
    d.line([(MARGIN, grid_top - 6), (W - MARGIN, grid_top - 6)], fill=RULE,
           width=2)
    col_w = (CW - 3 * 16) // 4  # 220
    cols = [
        [("EUROPE", RED, [
            "Russia bars Europe from Ukraine talks",
            "Russian drone flies over Moldova capital",
            "UK blacklists eight Israeli builders",
            "Depardieu admits sex-assault charge",
            "Five EU states plan Rwanda return hub",
            "Pattinson named the new James Bond",
            "COP31 draft urges faster fossil-fuel exit",
        ]),
         ("AFRICA", (46, 125, 50), [
            "DRC Ebola at record pace: 11,254 cases",
            "UN: 1,390 civilians killed in Sudan",
            "Drones killed 1,600+ in Sudan this year",
        ])],
        [("ASIA", (14, 107, 122), [
            "Japan scrambles jets as Russian planes intrude",
            "Taiwan halts Malaysia investment talks",
            "Mongolia\u2019s president resigns in scandal",
            "Trump lands in Manila for Quad summit",
            "Macron strolls Petaling Street in Malaysia",
            "Trump team eyes Kim meeting at APEC",
            "Bangkok building fire kills 11",
        ]),
         ("OCEANIA", (107, 63, 160), [
            "NZ dollar hits six-year low",
            "Santner out of India Tests, broken hand",
            "PNG\u2019s Marape: Taiwan move \u2018wasn\u2019t easy\u2019",
        ])],
        [("MIDDLE EAST", (179, 38, 30), [
            "IRGC says it seized a US drone near Qeshm",
            "LPG tanker hit off Oman; crew evacuated",
            "Saudi strike kills 7 at Hudaydah factory",
            "Houthis advance as Yemen army pulls back",
            "Settler mob kills 72-year-old in Jericho",
            "Israel freezes E1 settlement tender",
            "Eisenkot bloc elects Knesset speaker",
        ]),
         ("AFRICA", (46, 125, 50), [
            "WHO meets as Ebola second wave hits",
            "Sudan-Ethiopia tensions deepen",
            "WFP aids families fleeing Ethiopia strife",
        ])],
        [("AMERICAS", (20, 33, 61), [
            "Ecuador fishermen sue US over boat strike",
            "Pentagon fails audit for ninth year",
            "NSA internal network crashes",
            "Haitians rally for Salvadoran troops",
            "Brazil rout Singapore 7\u20130; Vin\u00edcius treble",
            "US air travellers warned of messy day",
            "Trump \u2018looking into\u2019 Iran dirty-bomb claim",
        ]),
         ("OCEANIA", (107, 63, 160), [
            "Qantas flight diverts to Auckland",
            "NZ publishes 58-nation visa list",
            "El Ni\u00f1o drought hits Fiji and Tonga",
        ])],
    ]
    ends = []
    for i, sections in enumerate(cols):
        cx = MARGIN + i * (col_w + 16)
        ends.append(draw_column(d, cx, grid_top, col_w, sections))
    grid_end = max(ends)
    assert grid_end <= 988, "grid overflow: ends %d" % grid_end

    # --- footer ---
    d.text((W // 2, 974),
           "All events happened or were first reported on Tuesday, 17 November 2026",
           font=font(SANS, 15), fill=GREY, anchor="ma")

    out = os.path.join(HERE, "entry.png")
    img.save(out, format="PNG", optimize=True)
    size = os.path.getsize(out)
    print("wrote %s: %s, %d bytes" % (out, img.size, size))
    assert img.size[0] <= 1024 and img.size[1] <= 1024
    assert size <= 1048576, "over 1 MiB!"


if __name__ == "__main__":
    main()
