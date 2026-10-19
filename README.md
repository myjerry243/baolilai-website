# Baolilai powder coating site (bilingual)

EN: `/`  ·  CN: `/cn/`  ·  generator: `build_site.py`

    cd /g/baolilai-site && python -m http.server 8099
    # http://127.0.0.1:8099/      (English)
    # http://127.0.0.1:8099/cn/   (中文)

## Launch checklist
1. Edit `CFG` at the top of `build_site.py`: email / phone / whatsapp / domain.
2. `python build_site.py` — regenerates both languages.
3. Replace the two `assets/img/application-*.jpg` with the plant's own photos
   (they are labelled "application reference" until then).
4. Colour card: `COLORS` list holds 24 RAL references + hex approximations.
   Add/remove entries there; both languages update automatically.

## Colour discipline (important)
RAL does not define sRGB values. The hex numbers in `COLORS` are approximations
for screen display only. Every page that shows a colour states that approval is
made on a sprayed panel against a physical RAL chip. Do not remove that sentence.

## Claim discipline
No AAMA / QUALICOAT / GSB / UL certificate is claimed anywhere. `quality.html`
states what is held and what is not, in both languages.

## Structure
- 12 pages × 2 languages, static, zero CDN dependencies
- `assets/css/site.css` — Archetype D tokens (bright natural, sage/grey-green)
- `assets/js/site.js` — header, hero carousel, reveal, counters, inquiry form
- `sitemap.xml` with both languages, `hreflang` tags on every page

## Live (GitHub Pages)
https://myjerry243.github.io/baolilai-website/  ·  中文： https://myjerry243.github.io/baolilai-website/cn/

Repo: https://github.com/myjerry243/baolilai-website (public, branch `main`, Pages from root `/`)

    # republish after a content change
    python build_site.py && python tools/make_tds.py
    git add <changed paths> && git commit -m "..." && git push

Pushing only whitelisted site files is deliberate — `_source/`, `media_src/` and
`storyboard/` are internal material and are gitignored.

## TDS PDFs (Rev. 2026-10)
`tds_data.py` holds the content, `tools/make_tds.py` renders `assets/tds/<CODE>_TDS.pdf`
(4 pages: EN 1-2, 中文 3-4, selectable text). Rebuild: `python tools/make_tds.py`.
Claim discipline: no AAMA/QUALICOAT/GSB/UL product certificate is claimed; the
4,000 h salt spray / 10-year Florida report belongs to the fluorocarbon system only.
