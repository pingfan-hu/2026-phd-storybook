#!/usr/bin/env python3
"""Generate the back-cover art (spread 24): the dissertation re-imagined as a
hand-painted top-down desk scene with simplified, legible title-page text.

Image models are unreliable about rotation direction and object sizing, so the
composition is assembled deterministically from two generated layers:

1. The dissertation document, viewed from directly above, perfectly straight on a
   pure white background, with the simplified title-page lettering. Generated with
   the GPT-Image backend (it renders in-image text far more reliably than Gemini).
2. The desk scene: top-down wooden desk with a coffee cup and fountain pen at the
   edges and an empty center. Generated with the Gemini backend (no text needed).

The document is then extracted from its white background, rotated exactly 30
degrees clockwise with PIL, given a soft drop shadow, and pasted onto the desk,
scaled so the whole document is fully visible. Final canvas is 8:9 (1024x1152),
the exact aspect of the book's right-hand illustration pane (5.5in x 6.1875in with
object-fit: cover), so nothing is cropped in the rendered PDF.

Run from the storybook root:
    python3 images/make_backcover.py
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageFilter

SKILL = Path.home() / ".claude/skills/ph-image"
sys.path.insert(0, str(SKILL))
from image_gemini import generate as generate_gemini  # noqa: E402
from image_gpt import generate as generate_gpt  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "images" / "spread-24.png"

TILT_DEG = 30                  # clockwise, applied via PIL
CANVAS_W, CANVAS_H = 1024, 1152  # 8:9, the illustration pane's exact aspect
BOOK_FRACTION = 0.86           # rotated book bounding box fits within this canvas share
WHITE_THRESHOLD = 240          # background detection for extracting the document
SHADOW_OFFSET = (14, 20)
SHADOW_BLUR = 18
SHADOW_ALPHA = 80

BOOK_PROMPT = (
    "A warm Studio Ghibli watercolor illustration, viewed from DIRECTLY ABOVE: a finished "
    "PhD dissertation, a THICK bound stack of paper, clearly several hundred pages, its "
    "layered page edges and cloth binding visible along the sides. The document lies "
    "PERFECTLY STRAIGHT and vertical, exactly aligned with the image edges, centered on a "
    "PURE WHITE background with no shadow, no desk, no other objects, nothing else at all. "
    "The top sheet is the title page, hand-lettered in clean, highly legible dark "
    "warm-brown serif lettering, perfectly horizontal lines, reading exactly this text and "
    "nothing else:\n\n"
    "SUSTAINABLE TRANSPORTATION,\nSUSTAINABLE RESEARCH\n(the main title, largest lettering)\n\n"
    "then below, in smaller lettering: 'By Pingfan Hu'\n\n"
    "then: 'A Dissertation for the Degree of\nDoctor of Philosophy'\n\n"
    "then: 'The George Washington University'\n\n"
    "then: '2026'\n\n"
    "Every word must be spelled exactly as given, clean and readable, with even spacing. "
    "At the bottom of the title page, below the text, one small painterly decoration: a "
    "sleek modern Tesla-like electric sedan (smooth aerodynamic body, minimal grille, "
    "small T-shaped badge) plugged into a small home charger. Soft hand-painted watercolor "
    "texture, warm palette of cream, sage green, and soft terracotta. No other text, no "
    "border, no frame, pure white background all around the document."
)

DESK_PROMPT = (
    "A warm Studio Ghibli watercolor illustration, viewed from DIRECTLY ABOVE: a bird's-eye "
    "top-down view of a wooden desk surface filling the entire frame edge to edge, "
    "continuous warm brown wood grain, soft lamplight falling across it. Near the UPPER "
    "RIGHT corner: a cup of coffee on a small saucer, a perfect circle seen from above, "
    "dark coffee with a subtle swirl. Along the LEFT edge: a simple elegant fountain pen "
    "resting on the wood, seen from above. The large CENTRAL area of the desk is completely "
    "EMPTY bare wood: no papers, no books, no other objects anywhere. Gentle hand-painted "
    "watercolor texture, warm palette of cream and wood brown. Absolutely no text, no "
    "border, no frame."
)


def extract_document(book_img: Image.Image) -> Image.Image:
    """Crop the document out of its pure-white background."""
    gray = book_img.convert("L")
    mask = gray.point(lambda p: 255 if p < WHITE_THRESHOLD else 0)
    bbox = mask.getbbox()
    if bbox is None:
        raise RuntimeError("Could not locate the document on the white background.")
    return book_img.crop(bbox)


def compose(book: Image.Image, desk: Image.Image) -> Image.Image:
    desk = desk.convert("RGB").resize((CANVAS_W, CANVAS_H), Image.LANCZOS)

    # Scale the book so its rotated bounding box fits within BOOK_FRACTION of canvas.
    rotated_probe = book.convert("RGBA").rotate(-TILT_DEG, expand=True)
    scale = min(CANVAS_W * BOOK_FRACTION / rotated_probe.width,
                CANVAS_H * BOOK_FRACTION / rotated_probe.height)
    book = book.resize((round(book.width * scale), round(book.height * scale)),
                       Image.LANCZOS)
    rotated = book.convert("RGBA").rotate(-TILT_DEG, expand=True,
                                          resample=Image.BICUBIC,
                                          fillcolor=(0, 0, 0, 0))

    shadow = Image.new("RGBA", rotated.size, (0, 0, 0, 0))
    alpha = rotated.split()[3].point(lambda a: SHADOW_ALPHA if a > 0 else 0)
    shadow.putalpha(alpha)
    shadow = shadow.filter(ImageFilter.GaussianBlur(SHADOW_BLUR))

    canvas = desk.convert("RGBA")
    x = (CANVAS_W - rotated.width) // 2
    y = (CANVAS_H - rotated.height) // 2
    canvas.alpha_composite(shadow, (x + SHADOW_OFFSET[0], y + SHADOW_OFFSET[1]))
    canvas.alpha_composite(rotated, (x, y))
    return canvas.convert("RGB")


def main() -> None:
    with tempfile.TemporaryDirectory() as td:
        book_path = Path(td) / "book.png"
        desk_path = Path(td) / "desk.png"
        generate_gpt(BOOK_PROMPT, book_path, aspect="2:3")
        generate_gemini(DESK_PROMPT, desk_path, aspect="4:5")
        book = extract_document(Image.open(book_path))
        desk = Image.open(desk_path)
    compose(book, desk).save(OUT)
    print(f"  OK   {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
