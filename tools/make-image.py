# make-image.py — draw the 20 November 2026 front page for news-image-20261120.
#
# One static PNG, 1024x1024, drawn with Pillow and Liberation Sans. No photo,
# no image model, no network: every fact below was checked by hand against
# reporting published on 20 November 2026 (see the SOURCES list), and the
# script only turns that fixed list into pixels. Run from the entry root:
#   python3 tools/make-image.py
# It writes entry.png next to main.ts, deterministically.
#
# STORY LIST — Friday 20 November 2026 (verified 21 Nov 2026 WIB)
#   Lead: Russia hits three bridges over the Dnipro in Kyiv overnight
#     (400+ drones, 110+ missiles; 8 killed across Ukraine) — Reuters,
#     20 Nov 2026; BBC via vocemundi.com. The "8 killed, 28 injured"
#     wording in the first draft was wrong: 8 were killed in total
#     across Ukraine (6 in Kyiv, 2 in Lviv) and 15 were hurt in Kyiv.
#   Poland: two Russian missiles and a jet drone cross into Poland;
#     NATO jets scramble; Tusk calls it a deliberate provocation;
#     Rutte calls it a "grave violation" — Reuters / AP, 20 Nov 2026.
#   COP31: talks run past their scheduled Friday close in Antalya;
#     the draft drops every mention of fossil fuels; Panama threatens
#     to block it — asiatoday.id / osna.fm, 20 Nov 2026.
#   Markets: Anthropic falls ~10% in premarket after its record debut;
#     S&P 500 down a sixth straight session; Nikkei nearly 5% — Reuters
#     via Kitco / TradingView, 20 Nov 2026.
#   Iran: Trump says he will decide nothing on new Iran strikes until
#     after 1 January 2027 — Reuters, 20 Nov 2026 (Axios, 19 Nov).
#   EU-UK: Britain and the EU agree to scrap food checks, link carbon
#     markets and open youth visas for 100,000 each way — AP, 20 Nov 2026.
#   Space: ESA-JAXA BepiColombo reaches Mercury after eight years and
#     6bn miles; orbit insertion due Saturday — Skeptic Society Magazine
#     / National Geographic, 20 Nov 2026.
#   Footer: Japan CPI keeps a December rate rise on track (Reuters,
#     20 Nov); GTA 6 tops $2.36bn in estimated first-day sales
#     (Sensor Tower via Reuters, 19-20 Nov); Italy fines Meta EUR 805m
#     (Morning Briefing #222, 20 Nov); Estonia to shut its Russia border
#     from 1 Dec (Reuters, 20 Nov); IMF warns global public debt nears
#     100% of GDP (Morning Briefing #222, 20 Nov).
#   Dropped from the first draft after checking: the Kenya Ebola panel
#     (the last patient was discharged on 11 Nov, not 20 Nov) and the
#     Houthi PIF-tower footer item (the strike was on 19 Nov).
#
# Layout (all pixels, canvas 1024x1024): cream page, navy masthead with a
# red tracked date line, a wide lead block with a navy picture square on
# the left, six panels in two rows of three, and a bold footer strip.

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "entry.png"

W, H = 1024, 1024
MARGIN = 28

CREAM = (247, 241, 229)
NAVY = (28, 43, 74)
RED = (168, 42, 42)
GOLD = (217, 164, 65)
GREEN = (46, 125, 79)
ORANGE = (192, 90, 30)
PURPLE = (91, 74, 138)
BODY = (58, 58, 58)
WHITE = (255, 255, 255)

LIB = "/usr/share/fonts/truetype/liberation"
DEJ = "/usr/share/fonts/truetype/dejavu"


def load(size, bold=False):
    """Liberation Sans, falling back to DejaVu Sans if it is missing."""
    stem = "LiberationSans-Bold.ttf" if bold else "LiberationSans-Regular.ttf"
    try:
        return ImageFont.truetype(f"{LIB}/{stem}", size)
    except OSError:
        stem = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
        return ImageFont.truetype(f"{DEJ}/{stem}", size)


def wrap(draw, text, font, max_w):
    """Greedy word wrap; returns a list of lines that fit max_w."""
    lines, cur = [], ""
    for word in text.split():
        trial = f"{cur} {word}".strip()
        if draw.textlength(trial, font=font) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_tracked(draw, cx, y, text, font, fill, tracking=10):
    """Draw text centred on cx with extra space between characters."""
    widths = [draw.textlength(ch, font=font) for ch in text]
    total = sum(widths) + tracking * (len(text) - 1)
    x = cx - total / 2
    for ch, w in zip(text, widths):
        draw.text((x, y), ch, font=font, fill=fill)
        x += w + tracking


def para(draw, x, y, text, font, fill, max_w, leading):
    """Draw a wrapped paragraph; returns the y just below the last line."""
    for line in wrap(draw, text, font, max_w):
        draw.text((x, y), line, font=font, fill=fill)
        y += leading
    return y


# ---- small geometric icons, drawn with plain Pillow shapes ----

def icon_bridge(d, cx, cy, s, color):
    """A bridge arch over a deck line."""
    d.arc([cx - s, cy - s, cx + s, cy + s], 180, 360, fill=color, width=6)
    for dx in (-s // 2, 0, s // 2):
        d.line([cx + dx, cy - s + 8, cx + dx, cy + s // 4], fill=color, width=5)
    d.line([cx - s - 6, cy + s // 4, cx + s + 6, cy + s // 4],
           fill=color, width=6)


def icon_target(d, cx, cy, s, color):
    """Concentric rings with a centre dot."""
    for r in (s, s * 2 // 3, s // 3):
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=color, width=5)
    d.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=color)


def icon_diamond(d, cx, cy, s, color):
    """A faceted gem: two triangles meeting at the middle."""
    d.polygon([(cx, cy - s), (cx + s // 2, cy), (cx, cy + s), (cx - s // 2, cy)],
              outline=color, width=5)
    d.line([cx, cy - s, cx, cy + s], fill=color, width=4)
    d.line([cx - s // 2, cy, cx + s // 2, cy], fill=color, width=4)


def icon_chart(d, cx, cy, s, color):
    """Rising bars crossed by a falling red trend line."""
    bars = [0.45, 0.7, 0.55, 0.95, 0.75]
    bw = s // 3
    x0 = cx - s
    for i, frac in enumerate(bars):
        top = cy + s // 2 - frac * s
        d.rectangle([x0 + i * (bw + 4), top, x0 + i * (bw + 4) + bw, cy + s // 2],
                    fill=color)
    d.line([x0, cy - s // 2, x0 + len(bars) * (bw + 4), cy + s // 3],
           fill=RED, width=5)


def icon_clock(d, cx, cy, s, color):
    """A clock face showing just past the hour."""
    d.ellipse([cx - s, cy - s, cx + s, cy + s], outline=color, width=5)
    d.line([cx, cy, cx, cy - s // 2], fill=color, width=5)
    d.line([cx, cy, cx + s // 2, cy + s // 4], fill=color, width=5)


def icon_rings(d, cx, cy, s, color):
    """Two interlocked rings."""
    d.ellipse([cx - s, cy - s // 2, cx, cy + s // 2], outline=color, width=5)
    d.ellipse([cx, cy - s // 2, cx + s, cy + s // 2], outline=color, width=5)


def icon_planet(d, cx, cy, s, color):
    """A planet on an elliptical orbit, with a small probe on the ring."""
    d.ellipse([cx - s - 14, cy - s // 3, cx + s + 14, cy + s // 3],
              outline=color, width=4)
    d.ellipse([cx - s // 2, cy - s // 2, cx + s // 2, cy + s // 2], fill=color)
    d.ellipse([cx + s - 2, cy - s // 3 - 4, cx + s + 8, cy - s // 3 + 6],
              fill=GOLD)


PANELS = [
    dict(accent=RED, kicker="POLAND · AIRSPACE", headline="MISSILES OVER POLAND",
         body="Two missiles and a jet drone cross into Poland overnight; "
              "NATO jets scramble.",
         icon=icon_target),
    dict(accent=GREEN, kicker="ANTALYA · CLIMATE", headline="COP31 TALKS OVERRUN",
         body="Talks run past their Friday close over a draft that drops "
              "every mention of fossil fuels.",
         icon=icon_diamond),
    dict(accent=NAVY, kicker="NEW YORK · MARKETS", headline="AI SELL-OFF DEEPENS",
         body="Anthropic slides 10% in premarket after its debut; stocks "
              "fall a sixth day, Nikkei nearly 5%.",
         icon=icon_chart),
    dict(accent=ORANGE, kicker="WASHINGTON · IRAN", headline="IRAN CALL DELAYED",
         body="Trump says he will decide nothing on new Iran strikes until "
              "after Jan. 1, despite pressure from Israel.",
         icon=icon_clock),
    dict(accent=NAVY, kicker="BRUSSELS · EUROPE", headline="EU AND UK SUMMIT",
         body="Britain and the EU agree to scrap food checks, link carbon "
              "markets and open youth visas.",
         icon=icon_rings),
    dict(accent=PURPLE, kicker="SPACE · MERCURY", headline="MERCURY AT LAST",
         body="After eight years and 6bn miles, the ESA-JAXA probe reaches "
              "Mercury; insertion is due Saturday.",
         icon=icon_planet),
]

LEAD_BODY = ("Russian missiles and drones hit three bridges over the Dnipro "
             "in Kyiv overnight, killing eight people across Ukraine in the "
             "biggest attack on the capital's crossings of the war.")

FOOTER = ("ALSO ON 20 NOVEMBER: Japan rate rise on track · GTA 6 tops $2.36bn "
          "· Italy fines Meta €805m · Estonia to shut Russia border · "
          "IMF warns debt nears 100% of GDP.")


def draw_panel(d, x, y, w, h, spec):
    """One white panel: coloured top bar, icon, kicker, headline, body."""
    accent = spec["accent"]
    d.rectangle([x, y, x + w, y + h], fill=WHITE, outline=NAVY, width=2)
    d.rectangle([x, y, x + w, y + 10], fill=accent)
    cx = x + w // 2
    spec["icon"](d, cx, y + 48, 26, accent)
    kicker_f = load(17, bold=True)
    d.text((x + 14, y + 82), spec["kicker"], font=kicker_f, fill=accent)
    head_f = load(27, bold=True)
    hy = y + 106
    for line in wrap(d, spec["headline"], head_f, w - 28):
        d.text((x + 14, hy), line, font=head_f, fill=NAVY)
        hy += 32
    body_f = load(17)
    lines = wrap(d, spec["body"], body_f, w - 28)
    assert len(lines) <= 3, f"panel body too long: {spec['headline']}"
    para(d, x + 14, hy + 6, spec["body"], body_f, BODY, w - 28, 22)


def main():
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)

    # Masthead.
    title_f = load(62, bold=True)
    d.text((W // 2, 22), "THE WORLD IN ONE DAY", font=title_f, fill=NAVY,
           anchor="ma")
    date_f = load(26, bold=True)
    draw_tracked(d, W // 2, 96, "FRIDAY · 20 NOVEMBER 2026", date_f, RED, 9)
    d.line([MARGIN, 132, W - MARGIN, 132], fill=NAVY, width=3)
    d.rectangle([MARGIN, 140, W - MARGIN, 148], fill=RED)

    # Lead block: navy picture square left, story right.
    lead_y, lead_h = 158, 272
    sq = 290
    d.rectangle([MARGIN, lead_y, MARGIN + sq, lead_y + lead_h], fill=NAVY)
    icon_bridge(d, MARGIN + sq // 2, lead_y + 118, 78, GOLD)
    city_f = load(26, bold=True)
    d.text((MARGIN + sq // 2, lead_y + 218), "KYIV", font=city_f, fill=WHITE,
           anchor="ma")
    tx = MARGIN + sq + 22
    tw = W - MARGIN - tx
    kick_f = load(22, bold=True)
    d.text((tx, lead_y + 8), "RUSSIA-UKRAINE WAR", font=kick_f, fill=RED)
    head_f = load(54, bold=True)
    hy = lead_y + 38
    for line in wrap(d, "RUSSIA STRIKES KYIV'S BRIDGES", head_f, tw):
        d.text((tx, hy), line, font=head_f, fill=NAVY)
        hy += 60
    body_f = load(24)
    lines = wrap(d, LEAD_BODY, body_f, tw)
    assert len(lines) <= 3, f"lead body wraps to {len(lines)} lines"
    para(d, tx, hy + 8, LEAD_BODY, body_f, BODY, tw, 31)
    d.rectangle([MARGIN, lead_y, W - MARGIN, lead_y + lead_h],
                outline=NAVY, width=2)

    # Six panels, two rows of three.
    gap = 16
    pw = (W - 2 * MARGIN - 2 * gap) // 3
    ph = 246
    py = lead_y + lead_h + 14
    for i, spec in enumerate(PANELS):
        x = MARGIN + (i % 3) * (pw + gap)
        y = py + (i // 3) * (ph + gap)
        draw_panel(d, x, y, pw, ph, spec)

    # Footer strip.
    fy = py + 2 * ph + gap + 12
    d.line([MARGIN, fy, W - MARGIN, fy], fill=NAVY, width=2)
    foot_f = load(19, bold=True)
    lines = wrap(d, FOOTER, foot_f, W - 2 * MARGIN)
    assert len(lines) <= 2, f"footer wraps to {len(lines)} lines"
    para(d, MARGIN, fy + 10, FOOTER, foot_f, NAVY, W - 2 * MARGIN, 25)

    img.save(OUT, "PNG")
    print(f"wrote {OUT} ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
