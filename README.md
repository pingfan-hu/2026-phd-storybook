# The Storybook of a PhD

An illustrated storybook retelling of Pingfan Hu's PhD dissertation, three
connected studies on battery electric vehicle (BEV) smart charging, told in
24 landscape spreads: prose on the left, warm watercolor art on the right.
The book comes in two synchronized editions, English and Chinese.

**Read it here: <https://pingfan-hu.github.io/2026-phd-storybook/>**

The site is an interactive flipbook with page-curl turning, an EN/中文
language toggle, and deep links (`?lang=cn`, `?page=9`). Print editions are
also available as PDFs:

- [English PDF](https://pingfan-hu.github.io/2026-phd-storybook/storybook.pdf)
- [Chinese PDF](https://pingfan-hu.github.io/2026-phd-storybook/storybook-cn.pdf)

Inspired by Rachel Coxcoon's dissertation storybook. The audience is
PhD-level readers: the content is simplified, the reader never is.

## How it's built

All text lives in `content/` (English and Chinese transcripts, plus the
source-facts sheet every number traces back to). Character portraits and
study charts are repainted into the book's warm style, composited into the
scene art in `images/`, and rendered by the scripts in `render/`:

```bash
python3 render/build.py              # English PDF  -> output/storybook.pdf
python3 render/build.py --lang cn    # Chinese PDF  -> output/storybook-cn.pdf
python3 render/build_book.py         # flipbook     -> output/book.html
bash render/deploy.sh                # rebuild everything + assemble docs/
```

See [CLAUDE.md](CLAUDE.md) for the full pipeline, structure, and house
style.

## Credits

- [StPageFlip](https://github.com/Nodlik/StPageFlip) (MIT) powers the
  page-curl flipbook.
- [Bootstrap Icons](https://icons.getbootstrap.com/) (MIT) provide the UI
  icons.
