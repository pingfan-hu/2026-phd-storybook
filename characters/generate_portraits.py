#!/usr/bin/env python3
"""Generate Studio Ghibli style character portraits from real photos.

Image-to-image via the ph-image Gemini backend: each real photo in
characters/original/ is repainted as a warm, hand-painted Studio Ghibli portrait
(saved to characters/cartoon/) while preserving the person's likeness (face,
hair, glasses, facial hair, notable clothing).

Run from the storybook root:
    python3 characters/generate_portraits.py            # all eight
    python3 characters/generate_portraits.py pingfan-hu # just one (by slug)
"""

from __future__ import annotations

import sys
from pathlib import Path

SKILL = Path.home() / ".claude/skills/ph-image"
sys.path.insert(0, str(SKILL))
from image_gemini import generate  # noqa: E402

CHARS = Path(__file__).resolve().parent
RES = CHARS / "original"
OUT = CHARS / "cartoon"

# Per-person hints reinforce the likeness the reference already carries.
PEOPLE = {
    "pingfan-hu": "an East Asian man with rectangular black glasses, short dark hair swept slightly up, and a grey wool scarf over an olive jacket, thoughtful and friendly",
    "john-helveston": "a YOUNG, fit, energetic white man in his late thirties (about 38), an early-career professor, with smooth healthy youthful skin and full firm cheeks, a taut jawline, bright lively eyes, and a fresh warm smile. His head is nearly bald from ordinary youthful male-pattern hair loss (NOT from age): a high receding hairline leaves the crown mostly bare, with a clearly visible band of very short light-brown hair (only lightly flecked with gray) around the sides and back; matte natural scalp, NOT a shiny bald dome, NOT a full head of hair. Light stubble, no glasses, a navy blazer over a navy polka-dot shirt. CRITICAL: he must look about 38 and youthful, like a young athletic assistant professor; absolutely NO wrinkles, NO deep nasolabial folds, NO hollow or gaunt cheeks, NO eye bags, NO forehead creases, NO age spots, NO sagging skin; never middle-aged, never elderly",
    "alan-jenn": "an East Asian man with short black hair cut close at the sides, olive-green rectangular glasses, clean-shaven, a broad warm smile, and a blue-and-white checked button-down shirt",
    "brian-tarroja": "a Filipino man with light tan skin, short black hair spiked up at the front, clean-shaven, a bright broad smile, and a light blue collared dress shirt",
    "eric-hittinger": "a white man with ginger-red hair and a short ginger beard, a brown tweed flat cap, and a tan jacket over a dark striped shirt, cheerful",
    "kate-forrest": "a white woman with long straight dark-brown center-parted hair, fair skin, blue-grey eyes, a warm broad smile, and a dark cardigan over a white top",
    "matthew-dean": "a white man with short reddish-brown hair, light stubble, brown eyes, a navy plaid blazer over a white shirt with a red-and-white patterned tie, confident smile",
    "bogdan-bunea": "a young man in his early twenties with light olive skin, voluminous dark-brown wavy hair, clear transparent-framed rectangular glasses, clean-shaven, a wide bright smile, and a black crew-neck t-shirt",
}

PROMPT = (
    "Studio Ghibli anime portrait, hand-painted in the warm, soft, painterly style of a "
    "Hayao Miyazaki film. Repaint {who} as a friendly Ghibli character, head and shoulders, "
    "facing the viewer with a gentle, warm expression. "
    "FAITHFULLY PRESERVE THE EXACT LIKENESS of the person in the reference photo: same face "
    "shape, same hairstyle and hair color, same glasses if any, same facial hair if any, same "
    "skin tone, and the same notable clothing. Translate the real photo into Ghibli illustration "
    "without changing who the person is. "
    "Soft watercolor cel-shading, gentle rounded features, expressive clear eyes, delicate "
    "painterly skin tones, soft rim light. Simple softly blurred warm background (muted cream, "
    "sage, or sky), no text, no logo, no border, no frame. Square 1:1 portrait, centered."
)


def run(slugs: list[str]) -> int:
    OUT.mkdir(exist_ok=True)
    failures = []
    for slug in slugs:
        ref = RES / f"{slug}.png"
        if not ref.exists():
            print(f"  SKIP {slug}: reference {ref.name} not found")
            failures.append(slug)
            continue
        out = OUT / f"{slug}.png"
        prompt = PROMPT.format(who=PEOPLE.get(slug, "the person in the reference photo"))
        print(f"  generating {slug} ...", flush=True)
        try:
            generate(prompt, out, ref_image=ref, aspect="1:1")
            print(f"  OK   {slug} -> characters/cartoon/{slug}.png")
        except Exception as exc:  # noqa: BLE001
            print(f"  FAIL {slug}: {exc}")
            failures.append(slug)
    print(f"\nDone. {len(slugs) - len(failures)}/{len(slugs)} succeeded.")
    if failures:
        print("Failed:", ", ".join(failures))
    return 1 if failures else 0


if __name__ == "__main__":
    requested = sys.argv[1:] or list(PEOPLE.keys())
    raise SystemExit(run(requested))
