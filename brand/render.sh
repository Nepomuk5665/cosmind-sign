#!/usr/bin/env bash
# Renders the icon files of overrides/public from the SVG sources in this folder, at the names and
# sizes DocuSeal's own files have (app/views/shared/_meta.html.erb, app/views/pwa/manifest.json.erb).
# The rendered files are committed; run this only after changing an SVG here. Needs rsvg-convert
# (librsvg) and ImageMagick 7 (`magick`).
#
#   brand/render.sh
set -euo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
public="$here/../overrides/public"

png() { rsvg-convert --width "$2" --height "$2" "$here/$1" --output "$public/$3"; }

# Browser tabs: the rounded tile, transparent corners.
cp "$here/icon.svg" "$public/favicon.svg"
png icon.svg 16 favicon-16x16.png
png icon.svg 32 favicon-32x32.png
png icon.svg 96 favicon-96x96.png
work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT
for size in 16 32 48; do rsvg-convert --width "$size" --height "$size" "$here/icon.svg" --output "$work/$size.png"; done
magick "$work/16.png" "$work/32.png" "$work/48.png" "$public/favicon.ico"

# Home screens: a full square, which iOS rounds itself.
png icon-square.svg 180 apple-icon-180x180.png
png icon-square.svg 180 apple-touch-icon.png
png icon-square.svg 180 apple-touch-icon-precomposed.png

# The link preview (og:image, 800 by 800 in _meta.html.erb).
png preview.svg 800 preview.png
