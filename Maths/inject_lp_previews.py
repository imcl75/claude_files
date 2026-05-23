#!/usr/bin/env python3
"""
inject_lp_previews.py

Post-processes a teaching PPTX to embed LP previews into the four
placeholder slides: Learning Paper 1, Marking Station 1,
Learning Paper 2, Marking Station 2.

Usage:
    python3 inject_lp_previews.py <teaching_pptx> <lp_combined_pptx>

The LP Combined PPTX has three slides:
    Slide 1 — Standard LP   (top half = LP1, bottom half = LP2)
    Slide 2 — Adapted LP    (not used here)
    Slide 3 — Marking Station (top half = MS1, bottom half = MS2)

The cut line is at exactly 50% of the LP slide height.
The script finds teaching slides by title (robust to slide count changes).
It overwrites the teaching PPTX in place.
"""

import sys
import os
import subprocess
import tempfile
from pathlib import Path
from PIL import Image
from pptx import Presentation
from pptx.util import Inches, Emu
from pptx.oxml.ns import qn
from lxml import etree

# Teaching slide → (lp_slide_index 0-based, crop_half)
SLIDE_MAP = {
    'Learning Paper 1':   (0, 'top'),
    'Marking Station 1':  (2, 'top'),
    'Learning Paper 2':   (0, 'bottom'),
    'Marking Station 2':  (2, 'bottom'),
}

# Image placement on teaching slide (inches)
IMG_TOP   = 1.05
IMG_LEFT  = 0.4
IMG_RIGHT = 12.93
IMG_BOT   = 7.30


def get_slide_title(slide):
    """Return plain text of the title shape, or ''."""
    for shape in slide.shapes:
        if shape.has_text_frame:
            tf = shape.text_frame
            text = tf.text.strip()
            if text in SLIDE_MAP:
                return text
    return ''


def convert_lp_to_images(lp_pptx, tmpdir, dpi=200):
    """Convert LP PPTX to per-slide JPEG images via soffice + pdftoppm."""
    pdf_out = Path(tmpdir) / (Path(lp_pptx).stem + '.pdf')

    r1 = subprocess.run(
        ['soffice', '--headless', '--convert-to', 'pdf',
         '--outdir', str(tmpdir), str(lp_pptx)],
        capture_output=True, text=True
    )
    if r1.returncode != 0 or not pdf_out.exists():
        # Try alternative soffice path
        r1 = subprocess.run(
            ['/usr/bin/soffice', '--headless', '--convert-to', 'pdf',
             '--outdir', str(tmpdir), str(lp_pptx)],
            capture_output=True, text=True
        )
    if not pdf_out.exists():
        raise RuntimeError(f"soffice failed to produce PDF.\nstdout: {r1.stdout}\nstderr: {r1.stderr}")

    prefix = str(Path(tmpdir) / 'lp_slide')
    r2 = subprocess.run(
        ['pdftoppm', '-jpeg', '-r', str(dpi), str(pdf_out), prefix],
        capture_output=True, text=True
    )
    if r2.returncode != 0:
        raise RuntimeError(f"pdftoppm failed:\n{r2.stderr}")

    images = sorted(Path(tmpdir).glob('lp_slide-*.jpg'))
    if not images:
        images = sorted(Path(tmpdir).glob('lp_slide*.jpg'))
    return images


def crop_half(img_path, half):
    """Crop image to top or bottom half. Returns PIL Image."""
    img = Image.open(img_path)
    w, h = img.size
    mid = h // 2
    if half == 'top':
        return img.crop((0, 0, w, mid))
    else:
        return img.crop((0, mid, w, h))


def clear_slide_content(slide):
    """Remove all shapes except the title from a slide."""
    to_remove = []
    for shape in slide.shapes:
        if shape.has_text_frame:
            text = shape.text_frame.text.strip()
            if text in SLIDE_MAP:
                continue  # keep the title
        to_remove.append(shape)
    sp_tree = slide.shapes._spTree
    for shape in to_remove:
        sp_tree.remove(shape._element)


def add_image_to_slide(slide, img_pil, slide_w_emu, slide_h_emu):
    """Add a PIL image to the slide, scaled to fill the usable area below the title."""
    import io
    buf = io.BytesIO()
    img_pil.save(buf, format='JPEG', quality=92)
    buf.seek(0)

    # Available area
    left_emu  = Inches(IMG_LEFT)
    top_emu   = Inches(IMG_TOP)
    right_emu = Inches(IMG_RIGHT)
    bot_emu   = Inches(IMG_BOT)
    avail_w   = right_emu - left_emu
    avail_h   = bot_emu - top_emu

    # Scale image to fit, preserving aspect ratio
    img_w, img_h = img_pil.size
    scale = min(avail_w / img_w, avail_h / img_h)
    new_w = int(img_w * scale)
    new_h = int(img_h * scale)

    # Centre within available area
    cx = left_emu + (avail_w - new_w) // 2
    cy = top_emu  + (avail_h - new_h) // 2

    slide.shapes.add_picture(buf, cx, cy, new_w, new_h)


def inject(teaching_pptx, lp_pptx):
    print(f"Teaching:  {teaching_pptx}")
    print(f"LP file:   {lp_pptx}")

    prs = Presentation(teaching_pptx)
    slide_w = prs.slide_width
    slide_h = prs.slide_height

    with tempfile.TemporaryDirectory() as tmpdir:
        print("Converting LP to images...")
        lp_images = convert_lp_to_images(lp_pptx, tmpdir)
        print(f"  Got {len(lp_images)} LP slide image(s)")

        if len(lp_images) < 3:
            raise RuntimeError(f"Expected at least 3 LP slide images, got {len(lp_images)}")

        injected = 0
        for slide in prs.slides:
            title = get_slide_title(slide)
            if title not in SLIDE_MAP:
                continue

            lp_idx, half = SLIDE_MAP[title]
            img = crop_half(lp_images[lp_idx], half)

            clear_slide_content(slide)
            add_image_to_slide(slide, img, slide_w, slide_h)
            injected += 1
            print(f"  Injected '{title}' ← slide {lp_idx+1} {half} half")

    prs.save(teaching_pptx)
    print(f"\nInjected {injected} LP previews.")
    print(f"Saved: {teaching_pptx}")
    return injected


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python3 inject_lp_previews.py <teaching_pptx> <lp_combined_pptx>")
        sys.exit(1)
    inject(sys.argv[1], sys.argv[2])
