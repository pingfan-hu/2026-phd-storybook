# TODO — finish the GitHub Pages deployment

Note to the next Claude session, from the session that relocated this project
here (2026-07-03). Read CLAUDE.md first for the project itself; this file is
only about finishing the deployment, delete it when done.

## Where things stand

- This repo (public, `pingfan-hu/2026-phd-storybook`) now contains the whole
  storybook project, relocated out of the private `papers` repo. Only the
  initial commit (README) is pushed; ALL project files are still uncommitted.
- The full pipeline was verified in this location on 2026-07-03: both PDFs
  build (fit check green) and `render/deploy.sh` assembled `docs/` (118 MB:
  index.html, book-assets/, the two PDFs, .nojekyll).
- Target site: https://pingfan-hu.github.io/2026-phd-storybook/ served from
  `docs/` on `main`.

## Remaining steps

1. Sanity-check `git status`, then commit everything (suggested: one
   `feat: storybook project + website` commit) and push to main.
   - Publishing publicly is CONFIRMED (2026-07-03): Pingfan verified the
     photos in `characters/original/` are all from public sources. No need
     to re-ask; just push.
   - Expect GitHub's >50 MB warnings for the two PDFs (54 MB each, in both
     output/ and docs/). Warning only; push succeeds. Git LFS is NOT wanted
     (Pages does not serve LFS files without extra setup).
2. Enable Pages (one-time, after the push):
   `gh api -X POST repos/pingfan-hu/2026-phd-storybook/pages -f 'source[branch]=main' -f 'source[path]=/docs'`
   If it 409s, Pages is already enabled; check with `gh api repos/pingfan-hu/2026-phd-storybook/pages`.
3. Verify the live site (give the first build a few minutes):
   the flipbook loads, art shows, EN/中文 toggle works, both PDF buttons
   download, `?lang=cn` and `?page=9` deep links work.
4. Polish README.md (currently a one-liner): what the book is, the live URL,
   the PDF links, how to build (see CLAUDE.md), and credit StPageFlip (MIT)
   and Bootstrap Icons (MIT).
5. Delete this TODO.md.

## Notes that save time

- `render/deploy.sh` is the only publish path: it rebuilds everything and
  regenerates `docs/` from scratch. Never hand-edit `docs/`.
- Builds need Chrome (headless, auto-detected; CHROME env var overrides).
  Image REgeneration (not needed for deployment) needs NANOBANANA_GEMINI_API_KEY.
- The old `papers` repo keeps the project's development history up to commit
  f6ae2b2; this repo starts fresh. If history is ever needed, it lives there.
- Future custom domain idea (not requested yet): book.pingfanhu.com via a
  CNAME file in docs/ + DNS.
