#!/usr/bin/env bash
# Build the storybook website into docs/ (served by GitHub Pages).
#
# This public repo is the website project: GitHub Pages serves the docs/
# folder on main. This script rebuilds the book, assembles docs/, and leaves
# the commit and push to you.
#
# One-time setup (after the first push that contains docs/):
#   gh api -X POST repos/pingfan-hu/2026-phd-storybook/pages \
#     -f 'source[branch]=main' -f 'source[path]=/docs'
#
# Site: https://pingfan-hu.github.io/2026-phd-storybook/
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DOCS="$ROOT/docs"

echo "== Building =="
python3 "$ROOT/render/build.py"
python3 "$ROOT/render/build.py" --lang cn
python3 "$ROOT/render/build_book.py"

echo "== Assembling docs/ =="
rm -rf "$DOCS"
mkdir -p "$DOCS"
# book.html reaches its assets via ../render/; on the site they sit alongside
sed 's|\.\./render/book-assets/|book-assets/|g' "$ROOT/output/book.html" > "$DOCS/index.html"
cp -R "$ROOT/render/book-assets" "$DOCS/book-assets"
cp "$ROOT/output/storybook.pdf" "$ROOT/output/storybook-cn.pdf" "$DOCS/"
touch "$DOCS/.nojekyll"

echo "docs/ assembled. Commit and push to publish:"
echo "  https://pingfan-hu.github.io/2026-phd-storybook/"
