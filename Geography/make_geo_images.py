#!/usr/bin/env python3
"""Generate two PNGs: Being a Geographer KC slide + geography cover placeholder."""
from reportlab.pdfgen import canvas as rlcanvas
from reportlab.lib.pagesizes import landscape
from PIL import Image
import io, os

W, H = 1920, 1080  # px at 96dpi

# ── colours ──────────────────────────────────────────────────────────
B1  = (23/255, 152/255, 211/255)   # #1798d3 Y4 blue
B2  = (12/255,  85/255, 150/255)
BL  = (0.92, 0.96, 1.00)
WH  = (1, 1, 1)
DG  = (0.10, 0.10, 0.10)

# ── helpers ───────────────────────────────────────────────────────────
def pdf_to_png(pdf_bytes, out_path, dpi=150):
    """Convert first page of PDF bytes to PNG via pdftoppm."""
    import subprocess, tempfile
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
        f.write(pdf_bytes); tmp = f.name
    pfx = tmp.replace('.pdf', '_pg')
    subprocess.run(['pdftoppm', '-jpeg', '-r', str(dpi), '-l', '1', tmp, pfx], check=True)
    imgs = sorted(f for f in os.listdir(os.path.dirname(pfx))
                  if os.path.basename(pfx) in f)
    pg = os.path.join(os.path.dirname(pfx), imgs[0])
    img = Image.open(pg).convert('RGB')
    img = img.resize((W, H), Image.LANCZOS)
    img.save(out_path, 'PNG')
    os.unlink(tmp); os.unlink(pg)
    print(f'  saved {out_path}')

def make_pdf_slide(draw_fn, out_path):
    buf = io.BytesIO()
    pw, ph = landscape((595.28, 841.89))  # landscape A4 pts
    c = rlcanvas.Canvas(buf, pagesize=(pw, ph))
    draw_fn(c, pw, ph)
    c.save()
    pdf_to_png(buf.getvalue(), out_path)

# ── 1. Being a Geographer KC slide ───────────────────────────────────
def draw_kc(c, W, H):
    M = 30
    # Full blue background
    c.setFillColorRGB(*B1)
    c.rect(0, 0, W, H, fill=1, stroke=0)

    # White content area
    c.setFillColorRGB(*WH)
    c.rect(M, M, W - 2*M, H - 2*M, fill=1, stroke=0)

    # Top bar
    c.setFillColorRGB(*B2)
    c.rect(M, H - M - 70, W - 2*M, 70, fill=1, stroke=0)
    c.setFillColorRGB(*WH)
    c.setFont('Helvetica-Bold', 28)
    c.drawString(M + 20, H - M - 70 + 22, 'Being a Geographer — Key Concepts')

    # Three concept boxes
    box_w = (W - 2*M - 40) / 3
    concepts = [
        ('Map Skills',
         ['Use atlases, globes and', 'digital maps to locate', 'places accurately.',
          '', 'Apply latitude, longitude,', 'hemisphere and time zone', 'knowledge.']),
        ('Observing',
         ['Use maps, photographs', 'and data to identify', 'physical and human', 'features.',
          '', 'Notice similarities', 'and differences between', 'places.']),
        ('Comparing and Concluding',
         ['Collect evidence from', 'more than one source.',
          '', 'Organise findings into', 'a reasoned comparison.',
          '', 'Communicate conclusions', 'using geographical', 'vocabulary.']),
    ]

    box_top = H - M - 80
    box_bot = M + 60
    box_h   = box_top - box_bot

    for i, (title, lines) in enumerate(concepts):
        bx = M + i * (box_w + 20)
        # Box fill
        shade = BL if i % 2 == 0 else (0.97, 0.99, 1.0)
        c.setFillColorRGB(*shade)
        c.rect(bx, box_bot, box_w, box_h, fill=1, stroke=0)
        # Colour header bar on box
        c.setFillColorRGB(*B1)
        c.rect(bx, box_top - 36, box_w, 36, fill=1, stroke=0)
        c.setFillColorRGB(*WH)
        c.setFont('Helvetica-Bold', 14)
        c.drawCentredString(bx + box_w/2, box_top - 36 + 11, title)
        # Content
        c.setFillColorRGB(*DG)
        c.setFont('Helvetica', 13)
        ty = box_top - 36 - 26
        for ln in lines:
            c.drawString(bx + 14, ty, ln)
            ty -= 20

    # Bottom strip
    c.setFillColorRGB(*B1)
    c.rect(M, M, W - 2*M, 50, fill=1, stroke=0)
    c.setFillColorRGB(*WH)
    c.setFont('Helvetica', 12)
    c.drawCentredString(W/2, M + 18,
        'Key Question:   Are England and Brazil different?   —   Year 4 Maple')

print('Creating Being a Geographer KC image...')
make_pdf_slide(draw_kc, '/home/claude/geo_kc.png')

# ── 2. Geography enquiry cover image ─────────────────────────────────
def draw_cover(c, W, H):
    # Blue background
    c.setFillColorRGB(*B1)
    c.rect(0, 0, W, H, fill=1, stroke=0)

    # Darker panel left third
    c.setFillColorRGB(*B2)
    c.rect(0, 0, W/3, H, fill=1, stroke=0)

    # White content area right
    c.setFillColorRGB(*WH)
    c.rect(W/3 + 10, 20, W*2/3 - 30, H - 40, fill=1, stroke=0)

    # Subject label
    c.setFillColorRGB(*B2)
    c.rect(W/3 + 10, H - 20 - 60, W*2/3 - 30, 60, fill=1, stroke=0)
    c.setFillColorRGB(*WH)
    c.setFont('Helvetica-Bold', 20)
    c.drawString(W/3 + 26, H - 20 - 60 + 18, 'Being a Geographer  —  Year 4 Maple')

    # Main title
    c.setFillColorRGB(*DG)
    c.setFont('Helvetica-Bold', 32)
    c.drawString(W/3 + 24, H - 130, 'Are England and')
    c.drawString(W/3 + 24, H - 170, 'Brazil different?')

    # Horizontal rule
    c.setStrokeColorRGB(*B1)
    c.setLineWidth(3)
    c.line(W/3 + 24, H - 185, W - 40, H - 185)

    # Phase label
    c.setFillColorRGB(*B1)
    c.setFont('Helvetica-Bold', 16)
    c.drawString(W/3 + 24, H - 216, 'Phase 1: Locate and Observe')

    # Globe / map icon text (placeholder)
    c.setFillColorRGB(0.70, 0.85, 0.95)
    c.roundRect(W/3 + 24, H - 420, W*2/3 - 70, 180, 10, fill=1, stroke=0)
    c.setFillColorRGB(*B2)
    c.setFont('Helvetica-Bold', 48)
    c.drawCentredString(W/3 + 24 + (W*2/3 - 70)/2, H - 350, '\ud83c\udf0e')  # globe emoji attempt
    c.setFont('Helvetica', 14)
    c.setFillColorRGB(*DG)
    c.drawCentredString(W/3 + 24 + (W*2/3 - 70)/2, H - 390,
        'Wallscourt Farm Academy  |  Term 6')

    # Left panel text
    c.setFillColorRGB(*WH)
    c.setFont('Helvetica-Bold', 18)
    # Vertical text approach — just write rotated
    c.saveState()
    c.translate(W/3 - 30, H/2)
    c.rotate(90)
    c.drawCentredString(0, 0, 'G E O G R A P H Y')
    c.restoreState()

print('Creating geography cover image...')
make_pdf_slide(draw_cover, '/home/claude/geo_cover.png')

print('Done.')
