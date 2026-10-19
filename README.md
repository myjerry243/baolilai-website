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
