#!/usr/bin/env python3
"""Generate the storybook scene illustrations in a consistent warm Ghibli style.

Each scene matches a spread's image brief in content/02-transcript.md. Four rules drive
this rewrite:

1. CHARTS ARE DRAWN, NOT PASTED. Earlier we composited the real study PNGs onto blank
   surfaces; they always read as flat stickers that did not fit their frames. Instead, each
   chart spread now describes a SIMPLE HAND-PAINTED ABSTRACTION of the real figure's shape
   (the flattened evening mountain, the steep cost curve, the saturating enrollment curve,
   the four-box flow, the survey form) right in the prompt, so the model paints it into the
   scene in the same watercolor style and it sits naturally on the surface. The abstraction
   conveys the IDEA of the real chart; it carries no text, numbers, or axis labels. The
   real figures in charts/ remain the source of truth for the shapes. No compositing step.

2. REAL cast, looking like themselves. Every named person uses a reference image: a single
   portrait (characters/cartoon/<slug>.png) for solo shots, or a tiled cast sheet
   (characters/sheets/<name>.png, a derived artifact: rebuild with
   characters/build_sheets.py before regenerating group scenes) for group shots. Pingfan
   uses characters/cartoon/pingfan-ref.png,
   the approved likeness cropped from spread-11, as the canonical face everywhere he appears.
   Group prompts name who is who in sheet order and forbid inventing strangers. Public crowds
   use natural, ordinary, realistic adults, never caricatures.

3. Scene-appropriate wardrobe. Refs are used for face/hair/glasses only, and each scene
   states its own clothing. Indoors and in mild weather: no coats, parkas, or scarves.

4. Pingfan is young. He is in his early thirties (about 33). Render him with smooth youthful
   skin and a relaxed, natural expression: no deep wrinkles, no heavy smile-fold lines, no
   strained or awkward grin.

The world stays physically real and at natural human scale: no giant wall-sized screens with
tiny people, no windows on interior walls, no floating coins/energy ribbons/glowing auras.

Run from the storybook root:
    python3 images/generate_scenes.py                 # all defined spreads
    python3 images/generate_scenes.py 06 08 18         # only these spreads
"""

from __future__ import annotations

import sys
from pathlib import Path

SKILL = Path.home() / ".claude/skills/ph-image"
sys.path.insert(0, str(SKILL))
from image_gemini import generate  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "images"
BASE = OUT / "base"
CHARS = ROOT / "characters" / "cartoon"
SHEETS = ROOT / "characters" / "sheets"
ASPECT = "4:5"  # portrait, fills the right-hand illustration pane

STYLE = (
    " Illustrated in a warm Studio Ghibli art style: soft hand-painted watercolor and gouache, "
    "gentle painterly light, clean linework, a cozy warm palette of cream, sage green, soft "
    "terracotta, and sky blue. IMPORTANT: Ghibli is only the painting STYLE. The world is "
    "realistic, ordinary, grounded, and present-day, rendered for grown-ups: real modern "
    "American architecture, contemporary electric cars, real charging equipment, and adult "
    "people in natural proportions and natural everyday clothing. This is NOT a cute children's "
    "picture book and NOT a fairy tale: no chibi or cartoon-cute faces, no toddlers or little "
    "children as the subject, no toy-like rounded cars, no storybook cottages. Keep a natural "
    "human scale: NO giant wall-sized screens or oversized displays with tiny people, NO "
    "impossible architecture such as a window set into an interior wall. Wardrobe matches the "
    "season and setting: indoors or in mild weather nobody wears winter coats, parkas, or "
    "scarves. Keep everything physically real: STRICTLY NO floating coins, NO floating money, "
    "NO glowing energy ribbons or streams, NO magical auras, NO giant symbolic scales, NO "
    "floating padlocks or lightbulbs, NO golden connecting threads, NO anthropomorphic sun or "
    "moon, NO spirit figures, NO whimsical creatures. "
    "Where the scene calls for a chart or diagram, paint it as a SIMPLE hand-drawn shape in "
    "the same soft watercolor style (clean lines, curves, bars, small boxes, arrows, or dots) "
    "that fits neatly inside its frame, screen, or board; it must look hand-painted, not like "
    "a pasted screenshot. "
    "No text, no words, no letters, no numbers, no axis labels, no captions, no UI text "
    "anywhere, including on any chart or screen. One cohesive full-bleed illustration, "
    "portrait composition, with no outer border around the whole picture."
)

# Wardrobe / likeness helpers -------------------------------------------------
PF_REF = (
    "Match Pingfan's face exactly to the reference image: the same young man, same "
    "rectangular black-framed glasses, same short dark hair, same slim smooth youthful face "
    "and calm gentle expression. He is about 33; no wrinkles, no heavy smile folds. Use the "
    "reference for face and hair only; take clothing from this scene's description."
)
INDOOR = (
    "Everyone is indoors in a comfortable room and nobody wears a coat, parka, or scarf. "
    "Pingfan wears a simple casual sweater or a plain buttoned shirt."
)
SHEET_RULE = (
    "The reference image is a cast sheet: real people's faces in a single row, left to right. "
    "Render ONLY these specific named people, matching each rendered face to the corresponding "
    "face in the sheet; do NOT invent, add, or substitute any other people. Give everyone "
    "natural, scene-appropriate everyday clothing; indoors nobody wears a coat or scarf."
)

PINGFAN = (
    "Pingfan, a youthful East Asian man in his early thirties (about 33) with rectangular "
    "black-framed glasses, short dark hair, and a slim, smooth, friendly face"
)
JOHN = (
    "John, a fit white man of about 38, an established professor: a mature, settled adult man, "
    "NOT a smooth-faced twenty-something and NOT an old man. Match his face EXACTLY to his "
    "reference face in the sheet and copy it faithfully: a lean angular face with prominent "
    "cheekbones and a defined jawline (lean and healthy, not chubby, not sickly-gaunt), fair "
    "skin, warm hazel eyes, light-brown fairly straight eyebrows, and a warm slight closed-mouth "
    "smile. His hairline is receding and his hair is closely buzzed all over: very short "
    "grayish-blond stubble-length hair covering the top and sides in a matte, natural way, "
    "thinning at the front, NOT a shiny bare bald dome and NOT a full head of hair. Light short "
    "stubble on his jaw, no glasses, a navy blazer over a navy polka-dot shirt. He should look "
    "youthful and energetic for an established professor around 38, never a college student and "
    "never elderly"
)
BOGDAN = (
    "Bogdan, a friendly young man in his early twenties with light olive skin, a full head of "
    "voluminous dark-brown wavy hair, and clear transparent-framed rectangular glasses (NOT thin "
    "round wire glasses, NOT light or reddish hair); clean-shaven, with a wide bright smile. Match "
    "his face to his reference face in the sheet"
)

# Alan Jenn genuinely resembles Pingfan (East Asian, glasses, short dark hair), so spell out
# what tells them apart to keep the two from blending in the group shot.
ALAN = (
    "Alan, an East Asian man with the same fair East Asian complexion as Pingfan (NOT tanned, NOT "
    "dark-skinned), of average build (NOT heavyset, NOT a fat face), clearly DIFFERENT from "
    "Pingfan: olive-green-framed rectangular glasses (not black), very short cropped hair with a "
    "slightly receding hairline, and a broad open warm smile, in a checked plaid collared shirt"
)

# Hand-drawn chart abstractions. Each describes the SHAPE of the real study figure as simple
# painterly line-art with no text or numbers, so it can be drawn into a frame/screen/board.
ABS_LOAD = (
    "a simple hand-painted line chart of a daily electricity-load curve: a tall rounded "
    "evening mountain with a soft pale-grey shaded area beneath it, and a second smooth line "
    "that pulls that evening peak down and lifts gently over the overnight stretch, so the "
    "mountain is visibly flattened; two distinct soft line colors (one dark, one sage green)"
)
ABS_DUCK = (
    "a simple hand-painted line chart of a daily electricity curve: one smooth dark line that "
    "sags into a low rounded belly through the middle of the chart, then rears up steeply on "
    "the right into a tall rounded crest, so the line's silhouette gently suggests a sitting "
    "duck (low belly, rising neck, rounded head); a second soft sage-green line flattens that "
    "tall crest and lifts the sagging belly. STRICTLY line-art only: do NOT draw an actual "
    "duck, bird, or any animal; just the two curves"
)
ABS_COST = (
    "a simple hand-painted line chart of three upward-sweeping curves that start low and flat "
    "on the left and then rise very steeply on the right (sharp diminishing returns), each in "
    "a soft distinct color (coral, green, blue)"
)
ABS_ENROLL = (
    "a simple hand-painted single concave curve that climbs steeply from the lower left and "
    "gradually levels off toward the upper right, like a gentle saturating S-curve, with a "
    "faint soft shaded band hugging the line"
)
ABS_CHOICE = (
    "a simple hand-painted on-screen choice question that clearly compares two program options: "
    "two upright option cards sit side by side, each card holding a short stack of two or three "
    "little attribute rows (each row a short label-dash on the left and a small value mark on "
    "the right) and, lower down, one slim horizontal battery bar split into three soft segments "
    "(grey, then orange, then green) with two tiny pointer marks above it; to the right of the "
    "two cards stands a slim narrow third column for a plain 'not interested' choice. It clearly "
    "reads as 'pick option one, option two, or neither', NOT as a random cluster of colored bars"
)
ABS_COST_BOARD = (
    "a simple clear cost curve drawn like a real chart: a faint L-shaped pair of axis lines (one "
    "vertical, one horizontal) meeting at the lower-left corner, and a single smooth curve that "
    "runs low and nearly flat along the bottom on the left, then bends and climbs steeply upward "
    "toward the upper right, with three or four small dot markers along it; it reads as a proper "
    "rising cost chart, not a random arc"
)
ABS_SURVEY = (
    "a simple hand-painted web-survey form: a short heading bar at the top, then three small "
    "circular radio buttons each beside a short horizontal line, and a small rounded button "
    "below them"
)
ABS_DOC_TO_SURVEY = (
    "a simple hand-painted before-and-after: on the left a plain document page covered in even "
    "horizontal lines of writing, then a soft arrow pointing right, then on the right a tidy "
    "web-survey form with a heading bar, three small radio-button rows, and a little button"
)
ABS_PIPELINE = (
    "a simple hand-painted laptop screen suggesting three things with soft shapes: a small "
    "branching version-history graph (dots joined by gently curving lines) on the left, a "
    "little survey-form preview (a heading line and three radio-button rows) in the middle, "
    "and a small database-cylinder icon on the right"
)

# A scene is (prompt, ref-path-or-None, to_base). to_base stays False now: charts are painted
# into each scene directly, so there is no separate base/composite step.
P = CHARS  # portraits
S = SHEETS  # cast sheets
PF = CHARS / "pingfan-ref.png"  # canonical approved Pingfan likeness (from spread-11)

SCENES: dict[str, tuple[str, Path | None, bool]] = {
    "01": (
        "The reference image is a STYLE GUIDE only: match its soft hand-painted watercolor "
        "washes, visible paper texture, gentle muted warm palette, loose painterly linework, "
        "and light airy feel EXACTLY, but do NOT copy its composition or content. Paint a NEW "
        "scene: a quiet contemporary American suburban street at golden dusk. Real present-day "
        "two-story suburban houses with siding, porches, and attached garages, warm light in "
        "the windows. A few modern electric cars are parked in driveways, plugged into "
        "wall-mounted home chargers. CHARGING CABLES MUST BE PHYSICALLY CORRECT: each "
        "charging car has exactly ONE cable, running in a single unbroken line from its "
        "wall-mounted charger to the car's charge port, both ends clearly attached. NO "
        "broken or cut cables, NO cables dangling loose or lying unconnected on the ground, "
        "NO extra cables, NO tangles; cars that are not charging have no cable at all. The "
        "charge port and connector are plain matte plastic, painted like the rest of the car: "
        "NO glowing green light in the charge port, NO neon glow anywhere in the scene. Soft "
        "golden dusk light, airy and warm, NOT dark, NOT high-contrast digital art. Calm, "
        "inviting, ordinary modern neighborhood.",
        OUT / "spread-04.png", False,
    ),
    "02": (
        f"{PINGFAN} sits at a wooden desk piled with papers, books, and an open laptop, glancing "
        "up from his work with a calm, gentle, natural expression and only the faintest soft "
        "smile (NOT a wide grin, NOT awkward). He looks fresh and youthful, smooth-skinned, "
        "early thirties, relaxed and at ease. A cozy modern home study with soft window light. "
        f"{INDOOR} A warm, believable portrait of a young PhD student. {PF_REF}",
        PF, False,
    ),
    "03": (
        "Two researchers sit at a modern cafe table covered with scattered notes, a laptop, and "
        "two coffee cups, leaning in, deep in animated conversation and losing track of time. "
        f"On the left, matching the LEFT face in the reference sheet, is {PINGFAN}, in a casual "
        f"sweater (no scarf, no coat). On the right, matching the RIGHT face in the sheet, is "
        f"{JOHN}. {SHEET_RULE} Warm afternoon light through a large cafe window.",
        S / "pair-pf-john.png", False,
    ),
    "04": (
        "A row of clean, well-kept present-day American suburban houses with fresh siding and "
        "tidy garages at six in the evening, soft golden dusk. Several modern electric cars are "
        "plugged into neat driveway home chargers at the same time, small charger lights lit. "
        "Warm light fills the windows, and tidy utility power lines and a single street "
        "transformer run along a smooth, clean road, carrying the busy evening load. Crisp, "
        "bright, freshly painted neighborhood feeling, NOT grimy, NOT cracked, NOT run-down; "
        "clean pavement, trim green lawns, a gently busy peak-hour mood.",
        None, False,
    ),
    "05": (
        "A real present-day suburban driveway at night, shown as two calm halves. On the left, a "
        "modern electric car is plugged into a wall-mounted home charger and charges quietly, a "
        "small steady green light on the charger. On the right, the same kind of car is "
        "connected by a thick cable to a home energy unit on the garage wall, suggesting power "
        "can also flow back from the car to the house. Real charging equipment, ordinary modern "
        "home, realistic night.",
        None, False,
    ),
    "06": (
        "A warm, realistic group portrait of about eight ordinary present-day adult electric-car "
        "owners standing proudly beside their modern electric cars in a sunny parking lot on a "
        "mild day. A natural mix of grown men and women of varied ages and backgrounds in "
        "everyday casual clothing (no winter coats, no scarves); relaxed, genuine smiles. Real "
        "contemporary cars with normal proportions. This is a believable photograph-like crowd "
        "of real adults, NOT a cartoon family scene and NOT children. "
        "In the upper corner of the sky hover two small, flat, recognizable social-media brand "
        "icons, side by side and painted in the same soft watercolor style: the Facebook icon (a "
        "rounded blue square with its white lowercase f) and the Instagram icon (a rounded "
        "warm-gradient square with a white camera outline), a gentle nod to how these owners "
        "were recruited. These two small brand icons are the ONLY floating elements and the ONLY "
        "letterform allowed in the picture; keep them small, tidy, and unobtrusive, with no "
        "other text anywhere.",
        None, False,
    ),
    "07": (
        f"{PINGFAN} sits at a kitchen table seen from the side, shown in profile (side view of his "
        "face) on the LEFT of the frame, facing right toward a tablet propped upright on the table "
        "in front of him. The camera is positioned slightly behind and above his shoulder so that "
        "BOTH his face in profile AND the full tablet screen are clearly visible at the same time: "
        "the tablet is angled so its glowing SCREEN faces him and is also legible to the viewer "
        "(we read the screen content, we do NOT see the blank back of the tablet). On the screen "
        f"is painted {ABS_CHOICE}. His hand reaches toward the screen as if about to tap a choice, "
        f"and his eyes look at the screen. {INDOOR} {PF_REF} Warm, realistic home, clean grounded "
        "composition; his profile and the choice screen are the two clear focal points.",
        PF, False,
    ),
    "08": (
        "A warm group of researchers around a large wooden table in a modern university meeting "
        "room, the table covered with a few printed papers showing simple hand-drawn line charts "
        "and a couple of laptops, mid-discussion and happy. Seven real people, matching the seven "
        f"faces in the reference sheet in order, left to right: {PINGFAN}; {JOHN}; {ALAN}; Brian, "
        "a Filipino-American man in a light blue shirt; Eric, a cheerful man with ginger hair and "
        "beard wearing a flat cap; Kate, a woman with long brown hair; and Matthew, a clean-cut "
        "man in a suit. Pingfan sits prominently near the center with an open laptop; his "
        "face must match the FIRST (leftmost) face in the reference sheet EXACTLY and look "
        "unmistakably like himself (rectangular black-framed glasses, slim smooth young East Asian "
        "face, short dark hair); John sits beside him. Make sure Pingfan and Alan look like two "
        "clearly different people, not lookalikes, and that Alan is plainly East Asian with the "
        "same fair complexion as Pingfan, not tanned and not heavyset. "
        f"{SHEET_RULE} On the upper-right wall hangs a single framed print in which is painted "
        f"{ABS_LOAD}. Contemporary academic setting.",
        S / "team08.png", False,
    ),
    "09": (
        "A person sleeps peacefully in a cozy modern bedroom at night. Through the window, their "
        "present-day electric car charges quietly in the driveway of a normal modern house, "
        "plugged into a wall charger with a small steady green light. Calm, reassuring, "
        "realistic night; just a real charger light, no glowing gauges.",
        None, False,
    ),
    "10": (
        "Night in a real suburban driveway. A present-day electric car is plugged into a "
        "wall-mounted home charger, charging. The adult owner stands nearby on the porch in a "
        "light jacket, smiling gently while checking a phone that shows a simple charging-savings "
        "screen with a small bar chart. Warm porch light, a real starry sky, ordinary modern "
        "house.",
        None, False,
    ),
    "11": (
        f"{PINGFAN} sits at his modern home-study desk, chin resting on his hand, looking "
        f"thoughtful as he weighs something up, wearing a plain sage-green sweater. {INDOOR} "
        f"{PF_REF} On the wall behind him hang TWO separate framed prints side by side, each "
        f"with a cream mat. In the LEFT frame is painted {ABS_LOAD}. In the RIGHT frame is "
        f"painted {ABS_COST}. Each painted chart sits centered and neatly within its own mat, "
        "filling the mat well. Warm study light, realistic and grounded.",
        PF, False,
    ),
    "12": (
        "A realistic researcher's workspace with no people in frame. On the wall is a large "
        "printed map of the United States with California marked sunny and New York marked "
        "snowy. On the desk sits an open laptop turned to face the viewer, and on its screen is "
        f"painted {ABS_ENROLL}. Beside the laptop are ordinary desk things: a coffee mug, a "
        "small notebook, and a potted plant. NO model towers, NO miniature pylons on the desk. "
        "Grounded, tidy, natural scale.",
        None, False,
    ),
    "13": (
        f"A modern room where {PINGFAN} stands looking up at a large framed print hanging on the "
        "wall at natural human scale (poster-sized, NOT a giant wall-sized screen). In the framed "
        f"print is painted {ABS_DUCK}, filling the mat neatly inside a simple dark frame. Through "
        "a normal window to one side, a real modern city at dusk. Pingfan is at natural size "
        f"relative to the print, seen from behind or in three-quarter view. {INDOOR} {PF_REF} "
        "Realistic, grounded, calm.",
        PF, False,
    ),
    "14": (
        "A modern academic room with two people, matching the two faces in the reference sheet. "
        f"Standing at a large wall-mounted whiteboard is {JOHN} (the RIGHT face in the sheet), "
        "turned slightly toward the board with one hand raised as if explaining. Seated at a "
        f"nearby table, watching and clearly looking like himself, is {PINGFAN} (the LEFT face "
        "in the sheet), in a plain casual sweater. On the whiteboard is drawn, in simple "
        f"marker-style line-art, {ABS_COST_BOARD}; John gestures at the steep rising part. Both "
        "are at natural scale. Make sure the seated man is unmistakably Pingfan (black-framed "
        f"glasses, slim smooth young face, short dark hair). {SHEET_RULE} No text or numbers on "
        f"the board. {INDOOR} Realistic, grounded.",
        S / "pair-pf-john.png", False,
    ),
    "15": (
        "A modern neighborhood at midnight. Many present-day electric cars have all started "
        "charging at once along the quiet streets and driveways, their small charger lights on, "
        "forming a new bright cluster of activity where it used to be dark and calm. A wry, "
        "gentle mood, as if the problem just moved to a new hour. Contemporary, realistic.",
        None, False,
    ),
    "16": (
        "Two contemporary winter-night scenes side by side. Left: a milder region's night, an "
        "open quiet modern street with plenty of room and a few electric cars charging calmly. "
        "Right: a cold snowy region's winter night, a modern street already busy and bright with "
        "warmly lit houses using heating, leaving little spare room. Realistic present-day "
        "neighborhoods.",
        None, False,
    ),
    "17": (
        f"{PINGFAN} sits at a modern home-study desk, frowning with mild frustration at his "
        "laptop. The laptop screen faces him at a three-quarter angle, showing a clunky, "
        "outdated survey-building website with a subscription-required paywall panel and a small "
        f"locked-feature padlock icon as part of the real on-screen software. {INDOOR} {PF_REF} A "
        "few crumpled notes nearby; warm, slightly exasperated but hopeful mood, realistic study.",
        PF, False,
    ),
    "18": (
        f"{PINGFAN} and {BOGDAN} sit side by side at a modern desk, each at an open laptop, "
        "collaborating happily. They are seen from the front, so each laptop is viewed from "
        "BEHIND: we see the back lid of each laptop (the plain logo side) facing us, and the "
        "screens are turned away toward the two men who are looking at them. Do NOT face the "
        "laptop screens toward the viewer. Pingfan, on the LEFT, matches the LEFT face in the "
        "reference sheet EXACTLY and is unmistakably himself: rectangular black-framed glasses, "
        "slim smooth young East Asian face, short dark hair; he faces his own laptop. Bogdan, on "
        f"the right, matches the RIGHT face. {SHEET_RULE} On the wall behind them hangs a single framed print "
        f"in which is painted {ABS_DOC_TO_SURVEY}, filling the mat neatly. {INDOOR} Warm, "
        "collaborative, realistic workspace.",
        S / "pair-pf-bogdan.png", False,
    ),
    "19": (
        "A close, realistic over-the-shoulder view of an open laptop on a wooden desk, the screen "
        f"facing the viewer. On the laptop screen is painted {ABS_PIPELINE}. A potted plant and a "
        "coffee mug sit beside the laptop. Calm, real modern desk, natural scale, grounded; no "
        "people's faces needed.",
        None, False,
    ),
    "20": (
        "A realistic modern open-plan office or lab at natural human scale. A few ordinary adult "
        "researchers sit at desks working on laptops. On one wall hangs a normal poster-sized "
        "printed world map (NOT a giant wall-sized screen), with small marker dots across many "
        "countries suggesting a worldwide community of users. The architecture is sane: solid "
        "interior walls with no windows set into them. Warm, grounded, believable, no sparkles.",
        None, False,
    ),
    "21": (
        "Inside a modern study, three framed prints hang in a neat row on the wall, each with a "
        "cream mat inside a simple dark wooden frame, a single tidy shelf running beneath them. "
        "Each frame holds a different simple hand-painted picture that fills its mat neatly. LEFT "
        "frame: a small warm group of a few diverse ordinary people standing together (the "
        f"people). MIDDLE frame: {ABS_LOAD} (the grid). RIGHT frame: an open laptop shown from "
        "the front with a simple survey form painted on its screen (a heading bar, three "
        "radio-button rows, and a small button) (the survey tool). Soft realistic study light, "
        "natural scale, grounded; no people in the room itself, no glowing panels.",
        None, False,
    ),
    "22": (
        "A calm, hopeful near-future modern town in the evening. Many present-day electric cars "
        "charge peacefully and at staggered times through the night along ordinary streets, warm "
        "steady lights in the windows and street lamps. Optimistic, realistic contemporary "
        "cityscape, soft Ghibli light.",
        None, False,
    ),
    "23": (
        "A warm, heartfelt gathering of exactly FIVE people standing close together around a "
        "table with an open book and a laptop in a modern room at golden hour, matching the five "
        "faces in the reference sheet in order, left to right. The leftmost person is "
        f"{PINGFAN}, in a simple sweater; his face must match the FIRST (leftmost) face in the "
        "reference sheet EXACTLY and look unmistakably like himself (rectangular black-framed "
        "glasses, slim smooth young East Asian face, short dark hair, chunky dark rectangular "
        f"frames exactly like the leftmost reference face). Beside him is {JOHN}. John must look "
        "about 38 here and match his reference face in the sheet exactly: his hair is closely "
        "BUZZED to stubble length all over with a receding hairline, NOT a full head of hair, NOT "
        "combed gray hair; his face is smooth and youthful with no wrinkles or age lines, neither "
        "a college student nor an older man in his fifties. Also present are Eric, "
        "a cheerful man with ginger hair and a ginger beard wearing a brown tweed FLAT CAP, a "
        "structured newsboy/driving cap with a short stiff front brim exactly as in his reference "
        "face (NOT a knit beanie, NOT a soft watch cap); Kate, a woman with "
        f"long brown hair; and {BOGDAN}. Render ONLY "
        "these five specific named people from the sheet and NOBODY else: no extra strangers, no "
        "unnamed guests, NO elderly people. Everyone looks like a real present-day adult, warm "
        f"and natural. {SHEET_RULE} {INDOOR} A scene of gratitude, realistic and contemporary.",
        S / "group23.png", False,
    ),
    # "24" is NOT generated here: the back cover is the dissertation title page
    # re-imagined in the same watercolor style WITH legible simplified text, which
    # needs the GPT-Image backend. It is produced by images/make_backcover.py.
}


def run(ids: list[str]) -> int:
    OUT.mkdir(exist_ok=True)
    BASE.mkdir(exist_ok=True)
    failures: list[str] = []
    for sid in ids:
        if sid not in SCENES:
            print(f"  SKIP {sid}: no scene defined")
            continue
        prompt, ref, to_base = SCENES[sid]
        dest = (BASE if to_base else OUT) / f"spread-{sid}.png"
        kwargs: dict = {"aspect": ASPECT}
        if ref is not None and ref.exists():
            kwargs["ref_image"] = ref
        elif ref is not None:
            print(f"  WARN {sid}: missing ref {ref}")
        tag = "base/" if to_base else ""
        print(f"  generating {tag}spread-{sid} ...", flush=True)
        try:
            generate(prompt + STYLE, dest, **kwargs)
            print(f"  OK   {tag}spread-{sid}.png")
        except Exception as exc:  # noqa: BLE001
            print(f"  FAIL spread-{sid}: {exc}")
            failures.append(sid)
    print(f"\nDone. {len(ids) - len(failures)}/{len(ids)} succeeded.")
    if failures:
        print("Failed:", ", ".join(failures))
    return 1 if failures else 0


if __name__ == "__main__":
    requested = sys.argv[1:] or list(SCENES.keys())
    raise SystemExit(run(requested))
