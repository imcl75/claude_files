"""
build_fractions_teaching.py
ALL 6 slides cloned from the uploaded working PPTX. No generator used anywhere.

  Slide 1: Mon I→M  (uploaded slide 1 — untouched)
  Slide 2: Mon M→I  (uploaded slide 2 — untouched)
  Slide 3: Tue I→M  (clone of slide 1 with Tue text+images)
  Slide 4: Tue M→I  (clone of slide 2 with Tue text+images)
  Slide 5: Wed I→M  (clone of slide 1 with Wed text+images)
  Slide 6: Wed M→I  (clone of slide 2 with Wed text+images)
"""

import os, re, zipfile, tempfile
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

WORKING_SRC = '/mnt/user-data/uploads/1782590393505_fractions_recap_animated.pptx'
OUT_FILE    = '/home/claude/T6W5_Fractions_Teaching.pptx'
CHART_DIR   = tempfile.mkdtemp(prefix='wfa_frac_t_')

# ── Data ──────────────────────────────────────────────────────────────────────
# I→M: ido=(N,D), youdo=[(N,D),...] — all days have 2 questions (matches slide 1)
I2M = {
    'Monday':    {'ido': (11,3), 'youdo': [(17,4),(13,5)]},
    'Tuesday':   {'ido': (19,6), 'youdo': [(23,5),(27,8)]},
    'Wednesday': {'ido': (31,8), 'youdo': [(22,5),(16,3)]},
}

# M→I: ido=(W,N,D), youdo=[(W,N,D),...] — all days have 2 questions (matches slide 2)
M2I = {
    'Monday':    {'ido': (2,3,5),  'youdo': [(3,1,4),(4,2,5)]},
    'Tuesday':   {'ido': (2,5,7),  'youdo': [(3,3,8),(5,1,6)]},   # Q2 added
    'Wednesday': {'ido': (5,1,3),  'youdo': [(4,3,7),(2,3,5)]},   # Q2 added
}

# rIds that are day-specific (same positions on both slides)
DAY_RIDS = ['rId3','rId4','rId7','rId8','rId10','rId11']

# Monday text to find-and-replace in each slide
MON_I2M_TEXTS = {
    'day':   'Monday',
    'step1': '11 \u00f7 3 = 3  remainder 2',   # TextBox 15 spid=16
}
MON_M2I_TEXTS = {
    'day':    'Monday',
    'step1':  '2 \u00d7 5 = 10',               # TextBox 15 spid=16
    'step2':  '10 + 3 = 13',                    # TextBox 17 spid=18
}

# ── PNG generators ────────────────────────────────────────────────────────────
def frac_png(num, den, tag, colour, fs=32, w=0.80, h=1.15):
    path = os.path.join(CHART_DIR, f'{tag}.png')
    fig, ax = plt.subplots(figsize=(w, h))
    fig.patch.set_facecolor('none'); ax.set_facecolor('none')
    ax.axis('off'); ax.set_xlim(0,1); ax.set_ylim(0,1)
    ax.text(0.5,0.78,str(num),ha='center',va='center',fontsize=fs,color=colour,fontweight='bold')
    ax.plot([0.06,0.94],[0.50,0.50],color=colour,lw=2.2)
    ax.text(0.5,0.14,str(den),ha='center',va='center',fontsize=fs,color=colour,fontweight='bold')
    plt.savefig(path,dpi=180,bbox_inches='tight',transparent=True); plt.close(fig)
    with open(path,'rb') as f: return f.read()

def mixed_png(W, num, den, tag, colour, fs=28, w=1.20, h=1.15):
    path = os.path.join(CHART_DIR, f'{tag}.png')
    fig, ax = plt.subplots(figsize=(w, h))
    fig.patch.set_facecolor('none'); ax.set_facecolor('none')
    ax.axis('off'); ax.set_xlim(0,1); ax.set_ylim(0,1)
    ax.text(0.20,0.50,str(W),ha='center',va='center',fontsize=fs+4,color=colour,fontweight='bold')
    ax.text(0.63,0.78,str(num),ha='center',va='center',fontsize=fs-2,color=colour,fontweight='bold')
    ax.plot([0.38,0.92],[0.50,0.50],color=colour,lw=2.0)
    ax.text(0.63,0.14,str(den),ha='center',va='center',fontsize=fs-2,color=colour,fontweight='bold')
    plt.savefig(path,dpi=180,bbox_inches='tight',transparent=True); plt.close(fig)
    with open(path,'rb') as f: return f.read()

def gen_i2m_images(day, data):
    N,D = data['ido']; W,R = divmod(N,D)
    imgs = {}
    imgs['rId3']  = frac_png(N,D, f'{day}_i2m_ido_q',  '#1798d3', fs=34)
    imgs['rId4']  = (frac_png(N,D,  f'{day}_i2m_ido_a', '#1A5C2A', fs=34) if R==0
                     else mixed_png(W,R,D, f'{day}_i2m_ido_a', '#1A5C2A', fs=30, w=1.20))
    for i,(Ny,Dy) in enumerate(data['youdo']):
        Wy,Ry = divmod(Ny,Dy)
        rq = f'rId{7 if i==0 else 10}'
        ra = f'rId{8 if i==0 else 11}'
        imgs[rq] = frac_png(Ny,Dy, f'{day}_i2m_q{i+1}_q', '#1798d3', fs=30, w=0.80, h=1.05)
        imgs[ra] = (frac_png(Ny,Dy,  f'{day}_i2m_q{i+1}_a', '#1A5C2A', fs=30, w=0.80, h=1.05) if Ry==0
                    else mixed_png(Wy,Ry,Dy, f'{day}_i2m_q{i+1}_a', '#1A5C2A', fs=26, w=1.20, h=1.05))
    return imgs

def gen_m2i_images(day, data):
    W,N,D = data['ido']; ans = W*D+N
    imgs = {}
    imgs['rId3'] = mixed_png(W,N,D, f'{day}_m2i_ido_q',  '#1798d3', fs=34, w=1.40, h=1.15)
    imgs['rId4'] = frac_png(ans,D,   f'{day}_m2i_ido_a',  '#1A5C2A', fs=34, w=0.80, h=1.15)
    for i,(Wy,Ny,Dy) in enumerate(data['youdo']):
        an = Wy*Dy+Ny
        rq = f'rId{7 if i==0 else 10}'
        ra = f'rId{8 if i==0 else 11}'
        imgs[rq] = mixed_png(Wy,Ny,Dy, f'{day}_m2i_q{i+1}_q', '#1798d3', fs=30, w=1.25, h=1.05)
        imgs[ra] = frac_png(an,Dy,      f'{day}_m2i_q{i+1}_a', '#1A5C2A', fs=30, w=0.75, h=1.05)
    return imgs

# ── Clone a slide ─────────────────────────────────────────────────────────────
def clone_slide(working_files, src_num, text_replacements, images, prefix, existing_media):
    """
    Clone slide src_num from working_files.
    text_replacements: {old_text: new_text}
    images: {rId: png_bytes}
    Returns (slide_xml_bytes, rels_str, {media_name: bytes})
    """
    xml  = working_files[f'ppt/slides/slide{src_num}.xml'].decode()
    rels = working_files[f'ppt/slides/_rels/slide{src_num}.xml.rels'].decode()

    # Text replacements
    for old, new in text_replacements.items():
        xml = xml.replace(f'<a:t>{old}</a:t>', f'<a:t>{new}</a:t>', 1)

    # Image replacements: update rels to point to new filenames
    new_media = {}
    for rId, png_bytes in images.items():
        candidate = f'{prefix}_{rId}.png'
        n = 0
        while candidate in existing_media:
            n += 1; candidate = f'{prefix}_{rId}_{n}.png'
        existing_media.add(candidate)
        new_media[candidate] = png_bytes
        # Update rels: replace old target for this rId with new filename
        rels = re.sub(
            rf'(Id="{rId}"[^>]+Target="\.\./media/)[^"]+(")',
            rf'\g<1>{candidate}\g<2>',
            rels
        )

    # Fix layout + remove notes
    rels = re.sub(r'Target="\.\./slideLayouts/slideLayout\d+\.xml"',
                  'Target="../slideLayouts/slideLayout13.xml"', rels)
    rels = re.sub(r'<Relationship[^>]+notesSlide[^>]+/>', '', rels)

    return xml.encode(), rels, new_media


def build():
    with zipfile.ZipFile(WORKING_SRC) as z:
        wf = {n: z.read(n) for n in z.namelist() if not n.endswith('/')}

    existing_media = {n.split('/')[-1] for n in wf if n.startswith('ppt/media/')}

    # ── Prepare 6 slides ──────────────────────────────────────────────────────
    slides = []  # (xml_bytes, rels_str, {media_name: bytes})

    # Fix rels helper for untouched slides
    def fix_rels(src_num):
        r = wf[f'ppt/slides/_rels/slide{src_num}.xml.rels'].decode()
        r = re.sub(r'Target="\.\./slideLayouts/slideLayout\d+\.xml"',
                   'Target="../slideLayouts/slideLayout13.xml"', r)
        r = re.sub(r'<Relationship[^>]+notesSlide[^>]+/>', '', r)
        return r

    # Slide 1: Mon I→M — untouched
    mon_media = {n.split('/')[-1]: wf[n] for n in wf if n.startswith('ppt/media/')}
    slides.append((wf['ppt/slides/slide1.xml'], fix_rels(1), mon_media))

    # Slide 2: Mon M→I — untouched (shares media already in mon_media)
    slides.append((wf['ppt/slides/slide2.xml'], fix_rels(2), {}))

    # Slide 3: Tue I→M — clone slide 1
    tu_i2m = I2M['Tuesday']; N,D = tu_i2m['ido']; W,R = divmod(N,D)
    xml, rels, media = clone_slide(
        wf, 1,
        {MON_I2M_TEXTS['day']: 'Tuesday',
         MON_I2M_TEXTS['step1']: f'{N} \u00f7 {D} = {W}  remainder {R}'},
        gen_i2m_images('tue', tu_i2m),
        'tue_i2m', existing_media
    )
    slides.append((xml, rels, media))

    # Slide 4: Tue M→I — clone slide 2
    tu_m2i = M2I['Tuesday']; Wm,Nm,Dm = tu_m2i['ido']; ans = Wm*Dm+Nm
    xml, rels, media = clone_slide(
        wf, 2,
        {MON_M2I_TEXTS['day']:   'Tuesday',
         MON_M2I_TEXTS['step1']: f'{Wm} \u00d7 {Dm} = {Wm*Dm}',
         MON_M2I_TEXTS['step2']: f'{Wm*Dm} + {Nm} = {ans}'},
        gen_m2i_images('tue', tu_m2i),
        'tue_m2i', existing_media
    )
    slides.append((xml, rels, media))

    # Slide 5: Wed I→M — clone slide 1
    we_i2m = I2M['Wednesday']; N,D = we_i2m['ido']; W,R = divmod(N,D)
    xml, rels, media = clone_slide(
        wf, 1,
        {MON_I2M_TEXTS['day']: 'Wednesday',
         MON_I2M_TEXTS['step1']: f'{N} \u00f7 {D} = {W}  remainder {R}'},
        gen_i2m_images('wed', we_i2m),
        'wed_i2m', existing_media
    )
    slides.append((xml, rels, media))

    # Slide 6: Wed M→I — clone slide 2
    we_m2i = M2I['Wednesday']; Wm,Nm,Dm = we_m2i['ido']; ans = Wm*Dm+Nm
    xml, rels, media = clone_slide(
        wf, 2,
        {MON_M2I_TEXTS['day']:   'Wednesday',
         MON_M2I_TEXTS['step1']: f'{Wm} \u00d7 {Dm} = {Wm*Dm}',
         MON_M2I_TEXTS['step2']: f'{Wm*Dm} + {Nm} = {ans}'},
        gen_m2i_images('wed', we_m2i),
        'wed_m2i', existing_media
    )
    slides.append((xml, rels, media))

    # ── Assemble output PPTX ──────────────────────────────────────────────────
    out = dict(wf)
    # Clear old slides
    for k in list(out):
        if re.match(r'ppt/slides/slide\d+', k): out.pop(k)

    all_media = {}
    for i,(xml_b,rels_s,mdict) in enumerate(slides):
        sn = i+1
        out[f'ppt/slides/slide{sn}.xml'] = xml_b
        out[f'ppt/slides/_rels/slide{sn}.xml.rels'] = (
            rels_s.encode() if isinstance(rels_s,str) else rels_s)
        all_media.update(mdict)
    for fname,data in all_media.items():
        out[f'ppt/media/{fname}'] = data

    SLIDE_REL = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide'

    # Rebuild presentation.xml slide list
    prs = out['ppt/presentation.xml'].decode()
    prs = re.sub(r'<p:sldIdLst>.*?</p:sldIdLst>',
                 '<p:sldIdLst>PLACEHOLDER</p:sldIdLst>', prs, flags=re.DOTALL)
    all_ids = [int(m) for m in re.findall(r'id="(\d+)"', prs)]
    next_id = max(all_ids, default=255) + 1
    entries = ''.join(f'<p:sldId id="{next_id+i}" r:id="rIdF{i+1}"/>'
                      for i in range(6))
    prs = prs.replace('PLACEHOLDER', entries)

    # Rebuild presentation rels
    prs_rels = out['ppt/_rels/presentation.xml.rels'].decode()
    prs_rels = re.sub(r'<Relationship[^>]+/slides/[^>]+/>', '', prs_rels)
    for i in range(6):
        sn = i+1
        prs_rels = prs_rels.replace(
            '</Relationships>',
            f'<Relationship Id="rIdF{sn}" Type="{SLIDE_REL}" '
            f'Target="slides/slide{sn}.xml"/></Relationships>')

    # Rebuild content types
    ct = out['[Content_Types].xml'].decode()
    ct = re.sub(r'<Override PartName="/ppt/slides/slide\d+\.xml"[^/]*/>', '', ct)
    for i in range(6):
        ct = ct.replace('</Types>',
            f'<Override PartName="/ppt/slides/slide{i+1}.xml" '
            f'ContentType="application/vnd.openxmlformats-officedocument'
            f'.presentationml.slide+xml"/></Types>')

    out['ppt/presentation.xml']            = prs.encode()
    out['ppt/_rels/presentation.xml.rels'] = prs_rels.encode()
    out['[Content_Types].xml']             = ct.encode()

    with zipfile.ZipFile(OUT_FILE, 'w', zipfile.ZIP_DEFLATED) as z:
        for name,data in out.items(): z.writestr(name, data)

    with zipfile.ZipFile(OUT_FILE) as z:
        n_slides = sum(1 for n in z.namelist() if re.match(r'ppt/slides/slide\d+\.xml$',n))
        n_media  = sum(1 for n in z.namelist() if n.startswith('ppt/media/'))
    print(f'Built: {OUT_FILE}  ({n_slides} slides, {n_media} media files)')

if __name__ == '__main__':
    build()
