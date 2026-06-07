"""
Writing Toolkit — Varjak's First Night Outside. A4 portrait.
Sections start directly below FA. Remaining space = write-your-own ruled box.
Verb bank anchored to bottom.
"""
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor, white
from reportlab.pdfbase.pdfmetrics import stringWidth

OUT = '/home/claude/T6W2_Writing_Toolkit.pdf'
W, H = A4; M = 1.4*cm

BLUE   = HexColor('#1798d3'); LBLUE  = HexColor('#daeef9')
PINK   = HexColor('#c0157b'); LPINK  = HexColor('#f9d6ec')
GREEN  = HexColor('#2bae62'); LGREEN = HexColor('#d4f2e2')
ORANGE = HexColor('#e57d24'); LORNG  = HexColor('#fde8d3')
PURPLE = HexColor('#6b3fa0'); LPURP  = HexColor('#ede0f7')
TEAL   = HexColor('#1a8a7a'); DBG    = HexColor('#ffffff')
DGREY  = HexColor('#333333'); GREY   = HexColor('#777777')
WBLUE  = HexColor('#f0f7ff')

c = canvas.Canvas(OUT, pagesize=A4)

def fr(x,y,w,h,col): c.setFillColor(col); c.rect(x,y,w,h,fill=1,stroke=0)
def hb(x,yt,w,h,col,txt,fs=9.5):
    fr(x,yt-h,w,h,col); c.setFillColor(white)
    c.setFont('Helvetica-Bold',fs); c.drawString(x+0.28*cm,yt-h+(h-fs)*0.44+1,txt)
def wrap(t,mw,sz=9.1):
    words=t.split(); lines,cur=[],''
    for w_ in words:
        test=(cur+' '+w_).strip()
        if stringWidth(test,'Helvetica',sz)<=mw: cur=test
        else:
            if cur: lines.append(cur); cur=w_
    if cur: lines.append(cur)
    return lines

BSIZE=9.1; LEAD=13.4; PAD=0.26*cm; IGAP=3.5; HH=0.5*cm

def sec_h(examples, mw):
    n=sum(len(wrap(e,mw)) for e in examples)
    return HH + n*LEAD + (len(examples)-1)*IGAP + 2*PAD

def draw_sec(title,examples,x,yt,w,hc,bc):
    mw=w-2*PAD-0.1*cm; h=sec_h(examples,mw)
    fr(x,yt-h,w,h-HH,bc); hb(x,yt,w,HH,hc,title)
    tx=x+PAD+0.1*cm; ty=yt-HH-PAD-BSIZE*0.72
    for ex in examples:
        lns=wrap(ex,mw)
        for i,ln in enumerate(lns):
            c.setFillColor(DGREY); c.setFont('Helvetica',BSIZE)
            c.drawString(tx,ty,('\u2022  ' if i==0 else '    ')+ln); ty-=LEAD
        ty-=IGAP
    return yt-h

# ── PAGE HEADER ──────────────────────────────────────────────────────
fr(0,H-1.1*cm,W,1.1*cm,BLUE); c.setFillColor(white)
c.setFont('Helvetica-Bold',13)
c.drawString(M,H-1.1*cm+0.38*cm,"Writing Toolkit  \u2014  Varjak\u2019s First Night Outside")
c.setFont('Helvetica',9.5)
c.drawRightString(W-M,H-1.1*cm+0.38*cm,"Year 4  |  T6W2  |  Being a Writer")
sy=H-1.1*cm-0.5*cm
c.setFillColor(DGREY); c.setFont('Helvetica-BoldOblique',8.5)
c.drawString(M,sy,"Use these examples to help build your narrative. Adapt them \u2014 make them your own.")

# ── FRONTED ADVERBIALS — full width ──────────────────────────────────
fa_top=sy-0.3*cm; fw=W-2*M
sub_names=['Place','Time','Manner']
sub_hc=[HexColor('#0f7abc'),TEAL,PURPLE]
sub_data=[
    ["At the far end of the alley,","Deep in the shadows,",
     "In the yellow glow of the lamp,","Beneath the cold brickwork,",
     "Beyond the edge of the light,"],
    ["As the night grew darker,","After what felt like hours,",
     "In that very moment,","Before he could take a breath,",
     "Just as dawn began to break,"],
    ["Trembling with every step,","Moving as quietly as he could,",
     "With his claws out and ears flat,","Without making a single sound,",
     "Pressing close against the wall,"],
]
sw3=(fw-0.06*cm)/3; sg3=0.03*cm; ssh=0.38*cm; ssz=9.1; slead=14.0
fa_body=ssh+5*slead+4*3+0.28*cm; fa_tot=HH+fa_body
fr(M,fa_top-fa_tot,fw,fa_body,LBLUE); hb(M,fa_top,fw,HH,BLUE,'Fronted Adverbials')
for i,(sn,shc,sexs) in enumerate(zip(sub_names,sub_hc,sub_data)):
    sx=M+i*(sw3+sg3); st=fa_top-HH
    fr(sx,st-ssh,sw3-0.01*cm,ssh,shc); c.setFillColor(white)
    c.setFont('Helvetica-Bold',9); c.drawString(sx+0.18*cm,st-ssh+0.09*cm,sn)
    ty=st-ssh-0.16*cm-ssz*0.72
    for ex in sexs:
        c.setFillColor(DGREY); c.setFont('Helvetica',ssz)
        c.drawString(sx+0.14*cm,ty,ex); ty-=slead
fa_bot=fa_top-fa_tot

# ── VERB BANK — anchored to bottom ───────────────────────────────────
footer_y=0.38*cm; vlead_=12.8; vsub_hh=0.38*cm; vbsize=8.8; vrows=6
verb_body=vsub_hh+vrows*vlead_+0.26*cm; verb_tot=HH+verb_body
verb_top_y=footer_y+verb_tot+0.12*cm

# ── TWO COLUMNS ───────────────────────────────────────────────────────
sec_gap=0.28*cm; inner_gap=0.26*cm
cg=0.32*cm; cw=(fw-cg)/2; c1=M; c2=M+cw+cg
mw=cw-2*PAD-0.1*cm

col_top=fa_bot-sec_gap

# left col: measure
examples_sim=["The car's headlights blazed like two trapped suns.",
     "The alleyway was as cold and still as the inside of a tomb.",
     "The dog's growl rumbled like distant thunder beneath the street.",
     "The shadows moved like something alive and hungry.",
     "The noise hit him like a wave crashing against rock.",
     "The city roared like a creature that had never once slept.",
     "The silence fell like the held breath of the whole world."]
examples_hyp=["His heart was beating hard enough to wake the whole city.",
     "The dog's growl was loud enough to shake the stones from the wall.",
     "He had never been so afraid in all his nine lives.",
     "The city seemed to stretch on for a thousand miles.",
     "The noise was so vast it filled every corner of the night."]
examples_all=["damp, dark doorways","shadows slipped and slid",
     "cold, cracked cobblestones","prowling, patient, perfectly still",
     "growling, glittering, glaring eyes","strange, shadowy, silent streets",
     "screeching, scattering, scrambling into the dark",
     "bold and brave and bristling with anger"]
examples_p3 =["The city was cold, loud and completely alive.",
     "He could smell rust, damp stone and something he had no name for.",
     "The streetlights flickered, buzzed and blinked out one by one.",
     "The gang was fast, silent and absolutely everywhere.",
     "He was afraid. He was alone. He was far from home.",
     "She crouched. She listened. She did not move.",
     "Varjak's claws were out. His teeth were bared. He was ready.",
     "The alley was dark. It was silent. It smelled of danger."]

h_sim=sec_h(examples_sim,mw)
h_hyp=sec_h(examples_hyp,mw)
h_all=sec_h(examples_all,mw)
h_p3 =sec_h(examples_p3 ,mw)

left_used  = h_sim + inner_gap + h_hyp
right_used = h_all + inner_gap + h_p3
left_bot   = col_top - left_used
right_bot  = col_top - right_used

# draw technique sections
y1=col_top; y1=draw_sec('Similes',  examples_sim,c1,y1,cw,PINK,  LPINK)
y1-=inner_gap
y1=draw_sec('Hyperbole',examples_hyp,c1,y1,cw,ORANGE,LORNG)

y2=col_top; y2=draw_sec('Alliteration',examples_all,c2,y2,cw,GREEN, LGREEN)
y2-=inner_gap
y2=draw_sec('Power of Three',examples_p3,c2,y2,cw,PURPLE,LPURP)

# ── DIRECT SPEECH — fills space above verb bank ─────────────────────
speech_top = min(y1,y2) - sec_gap
speech_bot = verb_top_y + sec_gap
sw_h = speech_top - speech_bot
if sw_h > 1.0*cm:
    # outer box
    fr(M, speech_bot, fw, sw_h - HH, LBLUE)
    hb(M, speech_top, fw, HH, BLUE, 'Direct Speech  \u2014  structures and speech verbs')
    # two sub-columns
    scol_gap = 0.32*cm; scol_w = (fw - scol_gap) / 2
    sc1 = M; sc2 = M + scol_w + scol_gap
    # sub-headers
    sc_hh = 0.36*cm
    sc_y  = speech_top - HH
    fr(sc1, sc_y - sc_hh, scol_w, sc_hh, BLUE)
    c.setFillColor(white); c.setFont('Helvetica-Bold', 8.2)
    c.drawString(sc1+0.18*cm, sc_y - sc_hh + 0.1*cm, 'Different ways to place the reporting clause')
    fr(sc2, sc_y - sc_hh, scol_w, sc_hh, TEAL)
    c.setFillColor(white); c.setFont('Helvetica-Bold', 8.2)
    c.drawString(sc2+0.18*cm, sc_y - sc_hh + 0.1*cm, 'Speech verbs')

    # Speech structure examples
    sp_examples = [
        ('Reporting clause AFTER the speech:',
         '\"You lost?\" she said.  /  \"Run,\" yelled Holly.'),
        ('Action BEFORE the speech:',
         'Varjak swallowed. \"I need your help,\" he stammered.'),
        ('Reporting clause SPLITS the speech:',
         '\"That,\" said Tam quietly, \"is a dog.\"'),
        ('No reporting clause (speaker is clear):',
         '\"Run!\"'),
        ('Reporting clause BEFORE the speech:',
         'Holly tilted her head and said, \"Dogs are different.\"'),
    ]
    sp_sz = 8.0; sp_lead = 11.0; sp_gap = 2
    tx1 = sc1 + 0.18*cm; mw1 = scol_w - 0.36*cm
    ty1 = sc_y - sc_hh - 0.14*cm - sp_sz*0.72
    for label, ex in sp_examples:
        c.setFillColor(HexColor('#0f5a8a')); c.setFont('Helvetica-Bold', 7.5)
        c.drawString(tx1, ty1, label); ty1 -= 10.5
        c.setFillColor(DGREY); c.setFont('Helvetica-Oblique', sp_sz)
        for ln in wrap(ex, mw1, sz=sp_sz):
            c.drawString(tx1 + 0.1*cm, ty1, ln); ty1 -= sp_lead
        ty1 -= sp_gap

    # Speech verbs word bank
    speech_verbs = [
        ('Quiet / calm',   ['whispered','murmured','breathed','replied','said']),
        ('Tense / urgent', ['stammered','faltered','urged','rasped','hissed']),
        ('Angry / harsh',  ['growled','snarled','snapped','spat','barked']),
        ('Loud / alarmed', ['yelled','called','cried','shouted','warned']),
    ]
    vb_sz = 8.2; vb_lead = 11.0; vb_cat_h = 0.28*cm
    tx2 = sc2 + 0.18*cm; mw2 = scol_w - 0.36*cm
    ty2 = sc_y - sc_hh - 0.12*cm - vb_sz*0.72
    cat_cols = [HexColor('#1a6e9a'), TEAL, HexColor('#7a3080'), ORANGE]
    for (cat, verbs), ccolor in zip(speech_verbs, cat_cols):
        # category mini-label
        c.setFillColor(ccolor); c.setFont('Helvetica-Bold', 7.5)
        c.drawString(tx2, ty2, cat); ty2 -= 10.0
        # verbs in a row
        vx_off = 0
        for verb in verbs:
            c.setFillColor(DGREY); c.setFont('Helvetica', vb_sz)
            vw = stringWidth(verb+'  ', 'Helvetica', vb_sz)
            if vx_off + vw > mw2:
                ty2 -= vb_lead; vx_off = 0
            c.drawString(tx2 + vx_off, ty2, verb)
            vx_off += vw
        ty2 -= vb_lead + vb_sz*0.3 + 2

# ── VERB BANK ─────────────────────────────────────────────────────────
vcats=[
    ('Moving through the city', BLUE,  LBLUE,
     ['crept','prowled','slunk','darted','pressed','scrambled',
      'skulked','edged','bolted','lurched','froze','vanished']),
    ('Sounds and voices',       GREEN, LGREEN,
     ['growled','screeched','hissed','yowled','rumbled','thundered',
      'scraped','clattered','echoed','stammered','snarled','rasped']),
    ('Showing fear or shock',   ORANGE,LORNG,
     ['swallowed','shuddered','bristled','flinched','tensed','hesitated',
      'faltered','trembled','braced','recoiled','clung','steadied']),
    ('Fighting and defending',  PURPLE,LPURP,
     ['swiped','lunged','dodged','leaped','launched','twisted',
      'sprang','blocked','spun','struck','scattered','retreated']),
]
vt=verb_top_y; vcw2=(fw-0.09*cm)/4; vcg2=0.03*cm
fr(M,vt-verb_tot,fw,verb_body,DBG); hb(M,vt,fw,HH,TEAL,'Powerful Verbs')
for i,(cat,hc,bc,verbs) in enumerate(vcats):
    vx=M+i*(vcw2+vcg2); vst=vt-HH
    fr(vx,vst-vsub_hh,vcw2-0.01*cm,vsub_hh,hc)
    c.setFillColor(white); c.setFont('Helvetica-Bold',7.8)
    c.drawString(vx+0.12*cm,vst-vsub_hh+0.09*cm,cat)
    half=len(verbs)//2
    for ci,col in enumerate([verbs[:half],verbs[half:]]):
        vvx=vx+ci*(vcw2/2)+0.08*cm; vy=vst-vsub_hh-0.14*cm-vbsize*0.72
        for verb in col:
            c.setFillColor(DGREY); c.setFont('Helvetica',vbsize)
            c.drawString(vvx,vy,verb); vy-=vlead_

# ── FOOTER ────────────────────────────────────────────────────────────
c.setFillColor(GREY); c.setFont('Helvetica',7)
c.drawString(M,footer_y,"T6W2  |  Being a Writer  |  Varjak Paw by S. F. Said")
c.drawRightString(W-M,footer_y,"Adapt these examples \u2014 change the details to fit your own narrative.")
c.save(); print("Saved:", OUT)
