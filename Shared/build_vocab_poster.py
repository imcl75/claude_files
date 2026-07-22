#!/usr/bin/env python3
"""
build_vocab_poster.py — WFA Top-10 Vocabulary Poster builder
Produces an A3 landscape HTML file from a vocabulary list.

Usage:
    from build_vocab_poster import build_vocab_poster
    build_vocab_poster(mtp, out_path)

    # or standalone:
    python3 build_vocab_poster.py england_brazil_mtp.json vocab_poster.html
"""

import os
import sys
import json
import re

# Year-group colours (Y4 = Maple LZ)
YG_COLOUR = {
    'Y3': '#c0157b',
    'Y4': '#1798d3',
    'Y5': '#e57d24',
    'Y6': '#2bae62',
}

# Default local image directory on Innes's Mac
_LOCAL_IMAGES = '/Users/innes/Pictures/claude-images'


def _slug(word):
    """Turn 'physical feature' → 'physical_feature' for image filename guessing."""
    return re.sub(r'[^a-z0-9]+', '_', word.lower()).strip('_')


def _image_src(entry, images_dir):
    """
    Resolve the best image src for a vocabulary entry.
    Priority:
      1. Explicit 'image' key in entry + images_dir
      2. Derived filename vocab_geo_{slug}.png in images_dir
      3. file:///Users/innes/Pictures/claude-images/ paths (absolute Mac path)
      4. Empty string (card renders without image)
    """
    word = entry.get('word', '')
    slug = _slug(word)

    candidates = []

    # Explicit filename
    if entry.get('image'):
        if images_dir:
            candidates.append(os.path.join(images_dir, entry['image']))
        # Always fall back to the Mac local path regardless
        candidates.append(f'file://{_LOCAL_IMAGES}/{entry["image"]}')

    # Derived filenames (vocab_geo_{slug}.png, then vocab_{slug}.png)
    for prefix in (f'vocab_geo_{slug}', f'vocab_{slug}'):
        if images_dir:
            candidates.append(os.path.join(images_dir, f'{prefix}.png'))
        candidates.append(f'file://{_LOCAL_IMAGES}/{prefix}.png')

    # Return first local file that actually exists, or first file:// path as fallback
    for c in candidates:
        if c.startswith('file://'):
            # Can't test this from the cloud; return it and let the browser resolve
            return c
        if os.path.exists(c):
            return c

    return ''


def _html(vocab_list, year_group, subject, key_question, images_dir):
    colour = YG_COLOUR.get(year_group, '#1798d3')
    subject_label = subject.replace('_', ' ')

    # Subject icon — try local images dir first, then Mac path
    icon_src = ''
    for candidate in [
        os.path.join(images_dir, f'icon_{subject}.png') if images_dir else '',
        f'file://{_LOCAL_IMAGES}/icon_{subject}.png',
    ]:
        if candidate:
            icon_src = candidate
            break

    cards_html = ''
    for entry in vocab_list[:10]:
        word = entry.get('word', '')
        defn = entry.get('definition', '')
        img  = _image_src(entry, images_dir)
        img_tag = (f'<img src="{img}" alt="{word}">' if img else
                   '<div class="img-placeholder"></div>')
        cards_html += f'''
    <div class="card">
      <div class="word">{word}</div>
      <div class="img-wrap">{img_tag}</div>
      <div class="def">{defn}</div>
    </div>'''

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Top 10 Words – {subject_label.title()} ({year_group})</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Fredoka+One&family=Nunito:wght@700;800&display=swap');

  :root {{
    --col: {colour};
    --hdr: 8vh;
  }}

  * {{ box-sizing: border-box; margin: 0; padding: 0; }}

  @page {{ size: A3 landscape; margin: 0; }}

  html, body {{
    width: 100vw;
    height: 100vh;
    overflow: hidden;
    background: #fff;
    font-family: 'Nunito', sans-serif;
  }}

  .poster {{
    width: 100vw;
    height: 100vh;
    border: 0.6vh solid var(--col);
    display: flex;
    flex-direction: column;
  }}

  .header {{
    background: var(--col);
    color: #fff;
    display: flex;
    align-items: center;
    padding: 0 2vw;
    gap: 1.5vw;
    height: var(--hdr);
    flex-shrink: 0;
  }}

  .subj-icon {{ height: 6vh; width: auto; flex-shrink: 0; filter: brightness(0) invert(1); }}

  .h-title {{
    font-family: 'Fredoka One', sans-serif;
    font-size: 4vh;
    text-decoration: underline;
    text-underline-offset: 2px;
    line-height: 1;
  }}

  .h-kq {{
    font-size: 1.8vh;
    font-weight: 700;
    margin-top: 0.3vh;
    opacity: 0.95;
  }}

  .grid {{
    flex: 1;
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    grid-template-rows: repeat(2, 1fr);
    min-height: 0;
  }}

  .card {{
    border-right: 0.2vh solid #aac8dc;
    border-bottom: 0.2vh solid #aac8dc;
    display: grid;
    grid-template-rows: 13% 1fr 22%;
    padding: 1vh 0.8vw;
    overflow: hidden;
    gap: 0;
    min-height: 0;
    background: #fff;
  }}

  .card:nth-child(n+6) {{ border-bottom: none; }}
  .card:nth-child(5n)  {{ border-right: none; }}

  .word {{
    font-family: 'Fredoka One', sans-serif;
    font-size: 3.4vh;
    color: var(--col);
    text-align: center;
    line-height: 1;
    display: flex;
    align-items: center;
    justify-content: center;
  }}

  .img-wrap {{
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 0;
    overflow: hidden;
    padding: 0.5vh 1vw;
  }}

  .img-wrap img {{
    max-width: 100%;
    max-height: 100%;
    object-fit: contain;
    display: block;
  }}

  .img-placeholder {{
    width: 60%;
    height: 70%;
    background: color-mix(in srgb, var(--col) 12%, #fff);
    border-radius: 0.8vh;
  }}

  .def {{
    font-size: 1.85vh;
    font-weight: 800;
    color: #111;
    text-align: center;
    line-height: 1.3;
    display: flex;
    align-items: center;
    justify-content: center;
  }}

  @media print {{
    html, body {{ -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
  }}
</style>
</head>
<body>
<div class="poster">

  <div class="header">
    <img class="subj-icon" src="{icon_src}" alt="{subject_label} icon">
    <div>
      <div class="h-title">Top 10 Words</div>
      <div class="h-kq">Being a {subject_label.title()} — {key_question}</div>
    </div>
  </div>

  <div class="grid">
{cards_html}
  </div>
</div>
</body>
</html>
'''


def build_vocab_poster(mtp_or_path, out_path, images_dir=None):
    """
    Build the Top-10 vocabulary poster HTML.

    Args:
        mtp_or_path:  path to MTP JSON or already-loaded MTP dict.
        out_path:     where to write the HTML file.
        images_dir:   directory for vocab images (optional; falls back to Mac local path).

    Returns:
        out_path on success.
    """
    if isinstance(mtp_or_path, (str, os.PathLike)):
        with open(mtp_or_path) as f:
            mtp = json.load(f)
    else:
        mtp = mtp_or_path

    vocab = mtp.get('vocabulary', [])
    if not vocab:
        print('  No "vocabulary" block in MTP — skipping vocab poster')
        return None

    year_group  = mtp.get('year_group', 'Y4')
    # subject: lesson-level → mtp top-level → fallback 'geographer'
    subject = (mtp['lessons'][0].get('subject') if mtp.get('lessons') else None) or \
              mtp.get('subject') or 'geographer'
    key_question = mtp.get('key_question', '')

    # Resolve images_dir
    if images_dir is None:
        images_dir = _LOCAL_IMAGES

    html = _html(vocab[:10], year_group, subject, key_question, images_dir)

    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f'  ✓ {out_path}')
    return out_path


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Usage: python3 build_vocab_poster.py <mtp.json> <out.html>')
        sys.exit(1)
    build_vocab_poster(sys.argv[1], sys.argv[2])
