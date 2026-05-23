"""
rapid_maths_generator.py  (v2 — with geometry image support)
=============================================================
INPUT:  rapid_maths_TEMPLATE.pptx
OUTPUT: Rapid_Maths_T5W1.pptx … Rapid_Maths_T5W5.pptx

AVAILABLE SHAPE KEYS:
    2D: equilateral_triangle, isosceles_triangle, right_triangle, scalene_triangle,
        square, rectangle, rhombus, parallelogram, trapezium, kite,
        pentagon, hexagon, octagon, circle
    3D: cube, cuboid, cylinder, cone, triangular_prism, square_pyramid
"""

import os, shutil, zipfile, io, math
from lxml import etree
from copy import deepcopy
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Polygon as MPoly, Ellipse

TEMPLATE_FILE = "rapid_maths_TEMPLATE.pptx"

NS_P   = "http://schemas.openxmlformats.org/presentationml/2006/main"
NS_A   = "http://schemas.openxmlformats.org/drawingml/2006/main"
NS_R   = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
NS_REL = "http://schemas.openxmlformats.org/package/2006/relationships"
NS_CT  = "http://schemas.openxmlformats.org/package/2006/content-types"
NS     = {"p":NS_P,"a":NS_A,"r":NS_R}

FILL_LIGHT="#DEECF8"; FILL_MID="#B5D1EF"; FILL_DARK="#8AB5E4"
EDGE_COL="#0070C0"; EDGE_LW=4.5

IMG_SLOTS = [
    {"img_x":2196768,"img_y":1231392,"img_w":1800000,"img_h":900000,
     "txt_box":"Text 5","new_txt_y":2151392,"new_txt_h":520688},
    {"img_x":2196768,"img_y":3232912,"img_w":1800000,"img_h":900000,
     "txt_box":"Text 9","new_txt_y":4152912,"new_txt_h":520688},
    {"img_x":2196768,"img_y":5234432,"img_w":1800000,"img_h":900000,
     "txt_box":"Text 13","new_txt_y":6154432,"new_txt_h":520688},
    {"img_x":7792768,"img_y":1231392,"img_w":2800000,"img_h":1600000,
     "txt_box":"Text 17","new_txt_y":2861392,"new_txt_h":811448},
    {"img_x":7792768,"img_y":4233672,"img_w":2800000,"img_h":1600000,
     "txt_box":"Text 21","new_txt_y":5863672,"new_txt_h":811448},
]

# ── Shape drawing ──────────────────────────────────────────────

def _save(fig):
    buf=io.BytesIO()
    fig.savefig(buf,format="png",dpi=150,bbox_inches="tight",
                facecolor="white",edgecolor="none",pad_inches=0.12)
    plt.close(fig); buf.seek(0); return buf.read()

def _reg(n,r=0.52,start=math.pi/2):
    return [(r*math.cos(start+2*math.pi*i/n),r*math.sin(start+2*math.pi*i/n)) for i in range(n)]

def _poly2d(verts):
    fig,ax=plt.subplots(figsize=(4.5,4)); ax.set_aspect("equal"); ax.axis("off")
    fig.patch.set_facecolor("white")
    ax.add_patch(MPoly(verts,closed=True,facecolor=FILL_LIGHT,edgecolor=EDGE_COL,linewidth=EDGE_LW))
    xs,ys=zip(*verts); pad=0.22
    ax.set_xlim(min(xs)-pad,max(xs)+pad); ax.set_ylim(min(ys)-pad,max(ys)+pad)
    return _save(fig)

def _ra_marker(ax,corner,l1,l2,s=0.075):
    def u(a,b): d=math.hypot(b[0]-a[0],b[1]-a[1]); return (b[0]-a[0])/d,(b[1]-a[1])/d
    v1,v2=u(corner,l1),u(corner,l2)
    sq=[(corner[0]+v1[0]*s,corner[1]+v1[1]*s),
        (corner[0]+v1[0]*s+v2[0]*s,corner[1]+v1[1]*s+v2[1]*s),
        (corner[0]+v2[0]*s,corner[1]+v2[1]*s)]
    ax.add_patch(MPoly(sq,closed=False,fill=False,edgecolor=EDGE_COL,linewidth=2.5))

def _faces3d(faces):
    fig,ax=plt.subplots(figsize=(4.5,4)); ax.set_aspect("equal"); ax.axis("off")
    fig.patch.set_facecolor("white"); all_x,all_y=[],[]
    for verts,fc in faces:
        all_x+=[v[0] for v in verts]; all_y+=[v[1] for v in verts]
        ax.add_patch(MPoly(verts,closed=True,facecolor=fc,edgecolor=EDGE_COL,linewidth=EDGE_LW,zorder=2))
    pad=0.18; ax.set_xlim(min(all_x)-pad,max(all_x)+pad); ax.set_ylim(min(all_y)-pad,max(all_y)+pad)
    return _save(fig)

def _rt():
    v=[(-0.5,-0.38),(0.52,-0.38),(-0.5,0.48)]
    fig,ax=plt.subplots(figsize=(4.5,4)); ax.set_aspect("equal"); ax.axis("off")
    fig.patch.set_facecolor("white")
    ax.add_patch(MPoly(v,closed=True,facecolor=FILL_LIGHT,edgecolor=EDGE_COL,linewidth=EDGE_LW))
    _ra_marker(ax,(-0.5,-0.38),(0.52,-0.38),(-0.5,0.48))
    ax.set_xlim(-0.72,0.74); ax.set_ylim(-0.58,0.68); return _save(fig)

def _cyl():
    fig,ax=plt.subplots(figsize=(4.5,4)); ax.set_aspect("equal"); ax.axis("off")
    fig.patch.set_facecolor("white"); r,yt,yb=0.38,0.38,-0.32
    ax.add_patch(mpatches.Rectangle((-r,yb),2*r,yt-yb,facecolor=FILL_MID,edgecolor="none",zorder=1))
    for xv in [-r,r]: ax.plot([xv,xv],[yb,yt],color=EDGE_COL,linewidth=EDGE_LW,zorder=3)
    ax.add_patch(Ellipse((0,yb),2*r,0.2,facecolor=FILL_DARK,edgecolor=EDGE_COL,linewidth=EDGE_LW,zorder=2))
    ax.add_patch(Ellipse((0,yt),2*r,0.2,facecolor=FILL_LIGHT,edgecolor=EDGE_COL,linewidth=EDGE_LW,zorder=4))
    ax.set_xlim(-0.65,0.65); ax.set_ylim(-0.58,0.62); return _save(fig)

def _cone():
    fig,ax=plt.subplots(figsize=(4.5,4)); ax.set_aspect("equal"); ax.axis("off")
    fig.patch.set_facecolor("white"); r,yb=0.42,-0.35
    ax.add_patch(MPoly([(-r,yb),(r,yb),(0,0.55)],closed=True,facecolor=FILL_MID,edgecolor=EDGE_COL,linewidth=EDGE_LW,zorder=1))
    ax.add_patch(Ellipse((0,yb),2*r,0.18,facecolor=FILL_DARK,edgecolor=EDGE_COL,linewidth=EDGE_LW,zorder=2))
    ax.set_xlim(-0.68,0.68); ax.set_ylim(-0.58,0.72); return _save(fig)

def _circle():
    fig,ax=plt.subplots(figsize=(4.5,4)); ax.set_aspect("equal"); ax.axis("off")
    fig.patch.set_facecolor("white")
    ax.add_patch(plt.Circle((0,0),0.48,facecolor=FILL_LIGHT,edgecolor=EDGE_COL,linewidth=EDGE_LW))
    ax.set_xlim(-0.72,0.72); ax.set_ylim(-0.72,0.72); return _save(fig)

SHAPES = {
    "equilateral_triangle": lambda: _poly2d([(-0.5,-0.29),(0.5,-0.29),(0,0.58)]),
    "isosceles_triangle":   lambda: _poly2d([(-0.42,-0.35),(0.42,-0.35),(0,0.65)]),
    "right_triangle":       _rt,
    "scalene_triangle":     lambda: _poly2d([(-0.58,-0.3),(0.5,-0.3),(0.08,0.52)]),
    "square":               lambda: _poly2d([(-0.45,-0.45),(0.45,-0.45),(0.45,0.45),(-0.45,0.45)]),
    "rectangle":            lambda: _poly2d([(-0.62,-0.35),(0.62,-0.35),(0.62,0.35),(-0.62,0.35)]),
    "rhombus":              lambda: _poly2d([(0,-0.52),(0.42,0),(0,0.52),(-0.42,0)]),
    "parallelogram":        lambda: _poly2d([(-0.5,-0.32),(0.28,-0.32),(0.5,0.32),(-0.28,0.32)]),
    "trapezium":            lambda: _poly2d([(-0.52,-0.32),(0.52,-0.32),(0.32,0.32),(-0.18,0.32)]),
    "kite":                 lambda: _poly2d([(0,-0.6),(0.4,0),(0,0.52),(-0.4,0)]),
    "pentagon":             lambda: _poly2d(_reg(5)),
    "hexagon":              lambda: _poly2d(_reg(6)),
    "octagon":              lambda: _poly2d(_reg(8)),
    "circle":               _circle,
    "cube":                 lambda: _faces3d([
        ([(-0.38,-0.35),(0.22,-0.35),(0.22,0.25),(-0.38,0.25)],FILL_MID),
        ([(0.22,-0.35),(0.58,-0.07),(0.58,0.53),(0.22,0.25)],FILL_DARK),
        ([(-0.38,0.25),(0.22,0.25),(0.58,0.53),(-0.02,0.53)],FILL_LIGHT)]),
    "cuboid":               lambda: _faces3d([
        ([(-0.5,-0.25),(0.32,-0.25),(0.32,0.18),(-0.5,0.18)],FILL_MID),
        ([(0.32,-0.25),(0.62,0.0),(0.62,0.43),(0.32,0.18)],FILL_DARK),
        ([(-0.5,0.18),(0.32,0.18),(0.62,0.43),(-0.2,0.43)],FILL_LIGHT)]),
    "triangular_prism":     lambda: _faces3d([
        ([(-0.45,-0.32),(0.15,-0.32),(-0.15,0.45)],FILL_MID),
        ([(0.15,-0.32),(0.52,-0.05),(0.22,0.72),(-0.15,0.45)],FILL_DARK)]),
    "square_pyramid":       lambda: _faces3d([
        ([(-0.38,-0.08),(0.52,-0.08),(0.1,0.75)],FILL_MID),
        ([(0.52,-0.08),(0.8,0.18),(0.1,0.75)],FILL_DARK),
        ([(-0.38,-0.08),(0.52,-0.08),(0.8,0.18),(0.04,0.18)],FILL_LIGHT)]),
    "cylinder":             _cyl,
    "cone":                 _cone,
}

# ── XML helpers ────────────────────────────────────────────────

def find_shape(tree,name):
    for sp in tree.findall(".//p:sp",NS):
        cnv=sp.find(".//p:cNvPr",NS)
        if cnv is not None and cnv.get("name")==name: return sp
    return None

def set_runs(sp,*texts):
    txBody=sp.find(".//p:txBody",NS)
    if txBody is None: return
    for para in txBody.findall("a:p",NS):
        runs=para.findall("a:r",NS)
        if not runs: continue
        while len(runs)<len(texts):
            clone=deepcopy(runs[-1]); runs[-1].addnext(clone); runs=para.findall("a:r",NS)
        for extra in runs[len(texts):]: para.remove(extra)
        runs=para.findall("a:r",NS)
        for run,text in zip(runs,texts):
            t=run.find("a:t",NS)
            if t is None: t=etree.SubElement(run,f"{{{NS_A}}}t")
            t.text=text
        break

def add_image_to_slide(tree,slot_idx,rid,elem_id):
    cfg=IMG_SLOTS[slot_idx]
    sp=find_shape(tree,cfg["txt_box"])
    if sp is not None:
        xfrm=sp.find(".//a:xfrm",NS)
        if xfrm is not None:
            off=xfrm.find("a:off",NS); ext=xfrm.find("a:ext",NS)
            if off is not None: off.set("y",str(cfg["new_txt_y"]))
            if ext is not None: ext.set("cy",str(cfg["new_txt_h"]))
        txBody=sp.find(".//p:txBody",NS)
        if txBody is not None:
            bodyPr=txBody.find("a:bodyPr",NS)
            if bodyPr is not None: bodyPr.set("anchor","t")
    pic_xml=(f'<p:pic xmlns:p="{NS_P}" xmlns:a="{NS_A}" xmlns:r="{NS_R}">'
             f'<p:nvPicPr><p:cNvPr id="{elem_id}" name="GeomImg_{slot_idx}"/>'
             f'<p:cNvPicPr><a:picLocks noChangeAspect="1"/></p:cNvPicPr><p:nvPr/></p:nvPicPr>'
             f'<p:blipFill><a:blip r:embed="{rid}"/><a:stretch><a:fillRect/></a:stretch></p:blipFill>'
             f'<p:spPr><a:xfrm><a:off x="{cfg["img_x"]}" y="{cfg["img_y"]}"/>'
             f'<a:ext cx="{cfg["img_w"]}" cy="{cfg["img_h"]}"/></a:xfrm>'
             f'<a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:noFill/></p:spPr></p:pic>')
    spTree=tree.find(".//p:spTree",NS)
    if spTree is not None: spTree.append(etree.fromstring(pic_xml))

def make_rels(img_refs=None):
    lines=['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
           '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">',
           '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout"'
           ' Target="../slideLayouts/slideLayout5.xml"/>']
    for rid,fname in (img_refs or []):
        lines.append(f'<Relationship Id="{rid}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image"'
                     f' Target="../media/{fname}"/>')
    lines.append("</Relationships>"); return "\n".join(lines)

def populate_q_slide(tree,day_num,qs):
    sp=find_shape(tree,"Title 26")
    if sp is not None: set_runs(sp,f"Rapid Maths \u2013 Day {day_num}")
    for lbl,qtxt,i in [("Text 4","Text 5",0),("Text 8","Text 9",1),("Text 12","Text 13",2),
                        ("Text 16","Text 17",3),("Text 20","Text 21",4)]:
        q=qs[i]; sp_l=find_shape(tree,lbl); sp_q=find_shape(tree,qtxt)
        if sp_l is not None: set_runs(sp_l,f"Q{q['q']}  ",q["topic"])
        if sp_q is not None: set_runs(sp_q,q["question"])

def populate_a_slide(tree,day_num,qs):
    sp=find_shape(tree,"Title 28")
    if sp is not None: set_runs(sp,f"Rapid Maths \u2013 Answers \u2013 Day {day_num}")
    for lbl,muted,ans,i in [("Text 4","Text 5","Text 6",0),("Text 9","Text 10","Text 11",1),
                              ("Text 14","Text 15","Text 16",2),("Text 19","Text 20","Text 21",3),
                              ("Text 24","Text 25","Text 26",4)]:
        q=qs[i]; sp_l=find_shape(tree,lbl); sp_m=find_shape(tree,muted); sp_a=find_shape(tree,ans)
        if sp_l is not None: set_runs(sp_l,f"Q{q['q']}  ",q["topic"])
        if sp_m is not None: set_runs(sp_m,q["question"])
        if sp_a is not None: set_runs(sp_a,q["answer"])

# ── Build ──────────────────────────────────────────────────────

def build(template_path,output_path,days,shape_cache):
    work="/tmp/rm_work"
    if os.path.exists(work): shutil.rmtree(work)
    with zipfile.ZipFile(template_path,"r") as z: z.extractall(work)
    slides_dir=os.path.join(work,"ppt/slides"); rels_dir=os.path.join(work,"ppt/slides/_rels")
    media_dir=os.path.join(work,"ppt/media")
    with open(os.path.join(slides_dir,"slide1.xml"),"rb") as f: s1=f.read()
    with open(os.path.join(slides_dir,"slide2.xml"),"rb") as f: s2=f.read()
    for sname,png in shape_cache.items():
        with open(os.path.join(media_dir,f"shape_{sname}.png"),"wb") as f: f.write(png)
    ct_path=os.path.join(work,"[Content_Types].xml")
    with open(ct_path,"rb") as f: ct=etree.fromstring(f.read())
    if not any(el.get("Extension")=="png" for el in ct):
        el=etree.SubElement(ct,f"{{{NS_CT}}}Default"); el.set("Extension","png"); el.set("ContentType","image/png")
    for day_idx,qs in enumerate(days):
        day_num=day_idx+1
        img_qs=[(i,qs[i]) for i in range(5) if "shape" in qs[i]]
        img_refs=[]
        for slot_idx,q in img_qs:
            rid=f"rId{2+len(img_refs)}"; img_refs.append((rid,f"shape_{q['shape']}.png")); q["_rid"]=rid
        fn_q=f"slide{day_idx*2+1}.xml"; fn_a=f"slide{day_idx*2+2}.xml"
        q_tree=etree.fromstring(s1); populate_q_slide(q_tree,day_num,qs)
        for (slot_idx,q),(rid,_) in zip(img_qs,img_refs):
            add_image_to_slide(q_tree,slot_idx,rid,elem_id=100+slot_idx*10)
        with open(os.path.join(slides_dir,fn_q),"wb") as f:
            f.write(etree.tostring(q_tree,xml_declaration=True,encoding="utf-8",standalone=True))
        with open(os.path.join(rels_dir,fn_q+".rels"),"w") as f: f.write(make_rels(img_refs))
        a_tree=etree.fromstring(s2); populate_a_slide(a_tree,day_num,qs)
        with open(os.path.join(slides_dir,fn_a),"wb") as f:
            f.write(etree.tostring(a_tree,xml_declaration=True,encoding="utf-8",standalone=True))
        with open(os.path.join(rels_dir,fn_a+".rels"),"w") as f: f.write(make_rels())
    prs_path=os.path.join(work,"ppt/presentation.xml")
    with open(prs_path,"rb") as f: prs=etree.fromstring(f.read())
    sldIdLst=prs.find(f"{{{NS_P}}}sldIdLst")
    for child in list(sldIdLst): sldIdLst.remove(child)
    for i in range(8):
        el=etree.SubElement(sldIdLst,f"{{{NS_P}}}sldId"); el.set("id",str(300+i))
        el.set(f"{{{NS_R}}}id",f"rId{20+i}")
    with open(prs_path,"wb") as f:
        f.write(etree.tostring(prs,xml_declaration=True,encoding="utf-8",standalone=True))
    prs_rels_path=os.path.join(work,"ppt/_rels/presentation.xml.rels")
    with open(prs_rels_path,"rb") as f: prs_rels=etree.fromstring(f.read())
    for el in list(prs_rels):
        if el.get("Type","").endswith("/slide"): prs_rels.remove(el)
    for i in range(8):
        el=etree.SubElement(prs_rels,f"{{{NS_REL}}}Relationship"); el.set("Id",f"rId{20+i}")
        el.set("Type","http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide")
        el.set("Target",f"slides/slide{i+1}.xml")
    with open(prs_rels_path,"wb") as f:
        f.write(etree.tostring(prs_rels,xml_declaration=True,encoding="utf-8",standalone=True))
    for el in list(ct):
        if "slides/slide" in el.get("PartName",""): ct.remove(el)
    for i in range(8):
        el=etree.SubElement(ct,f"{{{NS_CT}}}Override"); el.set("PartName",f"/ppt/slides/slide{i+1}.xml")
        el.set("ContentType","application/vnd.openxmlformats-officedocument.presentationml.slide+xml")
    with open(ct_path,"wb") as f:
        f.write(etree.tostring(ct,xml_declaration=True,encoding="utf-8",standalone=True))
    for i in range(1,3):
        for p in [os.path.join(work,f"ppt/notesSlides/notesSlide{i}.xml"),
                  os.path.join(work,f"ppt/notesSlides/_rels/notesSlide{i}.xml.rels")]:
            if os.path.exists(p): os.remove(p)
    with open(ct_path,"rb") as f: ct2=etree.fromstring(f.read())
    for el in list(ct2):
        if "notesSlide" in el.get("PartName",""): ct2.remove(el)
    with open(ct_path,"wb") as f:
        f.write(etree.tostring(ct2,xml_declaration=True,encoding="utf-8",standalone=True))
    with zipfile.ZipFile(output_path,"w",zipfile.ZIP_DEFLATED) as zout:
        for root,_,files in os.walk(work):
            for fname in files:
                full=os.path.join(root,fname); zout.write(full,os.path.relpath(full,work))
    print(f"  \u2713 {output_path}")

# ════════════════════════════════════════════════════════════════
# CONTENT — Term 5, Weeks 1–5
# No questions repeated from Wks 1–4 or within this term.
# Images: isosceles_triangle, cube (W1); rhombus, triangular_prism (W2);
#         pentagon, right_triangle (W3); hexagon, cone (W4); kite, cuboid (W5)
# ════════════════════════════════════════════════════════════════

WEEKS = {

"T5W1": [
  [{"q":1,"topic":"Place Value","question":"What is 1,000 more than 2,456?","answer":"3,456"},
   {"q":2,"topic":"Addition and Subtraction","question":"Calculate 5,263 + 3,184.","answer":"8,447"},
   {"q":3,"topic":"Multiplication and Division","question":"What is 11 \u00d7 4?","answer":"44"},
   {"q":4,"topic":"Geometry","question":"What type of triangle is this?","answer":"Isosceles triangle","shape":"isosceles_triangle"},
   {"q":5,"topic":"Fractions and Decimals","question":"What is 1/5 as a decimal?","answer":"0.2"}],
  [{"q":1,"topic":"Place Value","question":"Write six thousand and nine in numerals.","answer":"6,009"},
   {"q":2,"topic":"Multiplication and Division","question":"What is 56 \u00f7 7?","answer":"8"},
   {"q":3,"topic":"Geometry","question":"Lines that cross at right angles are called ___.","answer":"Perpendicular lines"},
   {"q":4,"topic":"Geometry","question":"What 3D shape is this?","answer":"Cube","shape":"cube"},
   {"q":5,"topic":"Addition and Subtraction","question":"Calculate 7,481 \u2212 3,256.","answer":"4,225"}],
  [{"q":1,"topic":"Place Value","question":"Round 8,264 to the nearest 100.","answer":"8,300"},
   {"q":2,"topic":"Addition and Subtraction","question":"Calculate 6,000 \u2212 3,247.","answer":"2,753"},
   {"q":3,"topic":"Fractions and Decimals","question":"How many tenths make one half?","answer":"5 tenths (0.5)"},
   {"q":4,"topic":"Measurement","question":"How many metres are in 2.5 km?","answer":"2,500 m"},
   {"q":5,"topic":"Geometry","question":"A rectangle is 9 cm long and 6 cm wide.\nWhat is its area?","answer":"54 cm\u00b2"}],
  [{"q":1,"topic":"Place Value","question":"What is the value of the digit 3 in 3,058?","answer":"3,000 (3 thousands)"},
   {"q":2,"topic":"Addition and Subtraction","question":"Calculate 4,516 + 2,738.","answer":"7,254"},
   {"q":3,"topic":"Multiplication and Division","question":"32 children are split equally into 4 groups.\nHow many in each group?","answer":"8 children"},
   {"q":4,"topic":"Geometry","question":"How many lines of symmetry does a square have?","answer":"4"},
   {"q":5,"topic":"Measurement","question":"A piece of string is 3 m long. Ben cuts off 85 cm.\nHow much string is left?","answer":"215 cm"}],
],

"T5W2": [
  [{"q":1,"topic":"Place Value","question":"What is 10 less than 5,003?","answer":"4,993"},
   {"q":2,"topic":"Addition and Subtraction","question":"Calculate 7,834 \u2212 4,956.","answer":"2,878"},
   {"q":3,"topic":"Multiplication and Division","question":"What is 12 \u00d7 3?","answer":"36"},
   {"q":4,"topic":"Geometry","question":"Name this quadrilateral.","answer":"Rhombus","shape":"rhombus"},
   {"q":5,"topic":"Fractions and Decimals","question":"Write in order, smallest first:\n0.5     0.1     0.75     0.25","answer":"0.1,  0.25,  0.5,  0.75"}],
  [{"q":1,"topic":"Place Value","question":"Write in order, smallest first:\n7,241    6,998    7,412    6,889","answer":"6,889   6,998   7,241   7,412"},
   {"q":2,"topic":"Multiplication and Division","question":"What is 64 \u00f7 8?","answer":"8"},
   {"q":3,"topic":"Geometry","question":"How many sides does a pentagon have?","answer":"5 sides"},
   {"q":4,"topic":"Measurement","question":"A bag of flour weighs 1.5 kg.\nHow many grams is that?","answer":"1,500 g"},
   {"q":5,"topic":"Addition and Subtraction","question":"Calculate 3,647 + 5,285.","answer":"8,932"}],
  [{"q":1,"topic":"Place Value","question":"What digit is in the hundreds place in 4,736?","answer":"7"},
   {"q":2,"topic":"Addition and Subtraction","question":"Calculate 9,001 \u2212 4,362.","answer":"4,639"},
   {"q":3,"topic":"Fractions and Decimals","question":"What fraction of 20 is 5?","answer":"1/4"},
   {"q":4,"topic":"Geometry","question":"What 3D shape is this?","answer":"Triangular prism","shape":"triangular_prism"},
   {"q":5,"topic":"Geometry","question":"How many faces does a triangular prism have?","answer":"5 faces"}],
  [{"q":1,"topic":"Place Value","question":"Round 3,455 to the nearest 1,000.","answer":"3,000"},
   {"q":2,"topic":"Multiplication and Division","question":"36 stickers shared equally between 9 friends.\nHow many each?","answer":"4 stickers each"},
   {"q":3,"topic":"Measurement","question":"How many minutes are in 2\u00bd hours?","answer":"150 minutes"},
   {"q":4,"topic":"Geometry","question":"A rectangle is 7 cm wide and has a perimeter of 26 cm.\nWhat is its length?","answer":"6 cm"},
   {"q":5,"topic":"Addition and Subtraction","question":"Calculate 6,215 + 1,847.","answer":"8,062"}],
],

"T5W3": [
  [{"q":1,"topic":"Place Value","question":"Write 9,070 in words.","answer":"nine thousand and seventy"},
   {"q":2,"topic":"Addition and Subtraction","question":"Calculate 2,836 + 4,597.","answer":"7,433"},
   {"q":3,"topic":"Multiplication and Division","question":"What is 8 \u00d7 4?","answer":"32"},
   {"q":4,"topic":"Geometry","question":"What is the name of this shape?","answer":"Pentagon","shape":"pentagon"},
   {"q":5,"topic":"Fractions and Decimals","question":"How many tenths make 1 whole?","answer":"10 tenths"}],
  [{"q":1,"topic":"Place Value","question":"What is 100 more than 7,906?","answer":"8,006"},
   {"q":2,"topic":"Multiplication and Division","question":"A class of 36 children splits into groups of 4.\nHow many groups?","answer":"9 groups"},
   {"q":3,"topic":"Geometry","question":"A 2D shape with straight sides is called a ___.","answer":"Polygon"},
   {"q":4,"topic":"Measurement","question":"A pool is 50 m long. Sam swims 4 lengths.\nHow far does she swim in total?","answer":"200 m"},
   {"q":5,"topic":"Addition and Subtraction","question":"Calculate 8,204 \u2212 3,576.","answer":"4,628"}],
  [{"q":1,"topic":"Place Value","question":"Write in order, greatest first:\n4,201    4,021    4,210    4,012","answer":"4,210   4,201   4,021   4,012"},
   {"q":2,"topic":"Addition and Subtraction","question":"Calculate 5,913 + 2,468.","answer":"8,381"},
   {"q":3,"topic":"Fractions and Decimals","question":"What is 7/10 as a decimal?","answer":"0.7"},
   {"q":4,"topic":"Geometry","question":"What type of triangle is this?","answer":"Right-angled triangle","shape":"right_triangle"},
   {"q":5,"topic":"Geometry","question":"A rectangle is 8 cm long and 7 cm wide.\nWhat is its area?","answer":"56 cm\u00b2"}],
  [{"q":1,"topic":"Place Value","question":"What is 1,000 less than 8,300?","answer":"7,300"},
   {"q":2,"topic":"Multiplication and Division","question":"What is 36 \u00f7 4?","answer":"9"},
   {"q":3,"topic":"Geometry","question":"What do we call the corners of a 3D shape?","answer":"Vertices (or vertex)"},
   {"q":4,"topic":"Fractions and Decimals","question":"Which is larger, 3/4 or 1/2?\nUse decimals to explain.","answer":"3/4  (0.75 > 0.5)"},
   {"q":5,"topic":"Measurement","question":"School starts at 9:00 am and ends at 3:15 pm.\nHow long is the school day?","answer":"6 hours 15 minutes"}],
],

"T5W4": [
  [{"q":1,"topic":"Place Value","question":"Write seven thousand, four hundred and eight in numerals.","answer":"7,408"},
   {"q":2,"topic":"Addition and Subtraction","question":"Calculate 6,427 + 2,854.","answer":"9,281"},
   {"q":3,"topic":"Multiplication and Division","question":"What is 11 \u00d7 7?","answer":"77"},
   {"q":4,"topic":"Geometry","question":"What is the name of this shape?","answer":"Hexagon","shape":"hexagon"},
   {"q":5,"topic":"Fractions and Decimals","question":"What is 3/10 as a decimal?","answer":"0.3"}],
  [{"q":1,"topic":"Place Value","question":"Round 5,750 to the nearest 100.","answer":"5,800"},
   {"q":2,"topic":"Multiplication and Division","question":"There are 7 days in a week.\nHow many days in 8 weeks?","answer":"56 days"},
   {"q":3,"topic":"Geometry","question":"How many right angles does a rectangle have?","answer":"4 right angles"},
   {"q":4,"topic":"Measurement","question":"A recipe needs 750 ml of milk.\nHow much is left in a 1-litre carton?","answer":"250 ml"},
   {"q":5,"topic":"Addition and Subtraction","question":"Calculate 7,100 \u2212 4,386.","answer":"2,714"}],
  [{"q":1,"topic":"Place Value","question":"What is 10 more than 9,995?","answer":"10,005"},
   {"q":2,"topic":"Addition and Subtraction","question":"Calculate 3,728 + 5,647.","answer":"9,375"},
   {"q":3,"topic":"Fractions and Decimals","question":"What is 9/10 as a decimal?","answer":"0.9"},
   {"q":4,"topic":"Geometry","question":"What 3D shape is this?","answer":"Cone","shape":"cone"},
   {"q":5,"topic":"Geometry","question":"A square has a perimeter of 32 cm.\nHow long is each side?","answer":"8 cm"}],
  [{"q":1,"topic":"Place Value","question":"What is the value of the digit 6 in 6,842?","answer":"6,000 (6 thousands)"},
   {"q":2,"topic":"Multiplication and Division","question":"What is 24 \u00f7 3?","answer":"8"},
   {"q":3,"topic":"Addition and Subtraction","question":"Calculate 4,963 + 2,175.","answer":"7,138"},
   {"q":4,"topic":"Geometry","question":"What is a flat surface on a 3D shape called?","answer":"A face"},
   {"q":5,"topic":"Measurement","question":"How many centimetres are in 4.8 metres?","answer":"480 cm"}],
],

"T5W5": [
  [{"q":1,"topic":"Place Value","question":"Write in order, greatest first:\n3,099    3,909    3,990    3,009","answer":"3,990   3,909   3,099   3,009"},
   {"q":2,"topic":"Addition and Subtraction","question":"Calculate 8,436 \u2212 3,879.","answer":"4,557"},
   {"q":3,"topic":"Multiplication and Division","question":"What is 12 \u00d7 6?","answer":"72"},
   {"q":4,"topic":"Geometry","question":"Name this quadrilateral.","answer":"Kite","shape":"kite"},
   {"q":5,"topic":"Fractions and Decimals","question":"What is 2/5 as a decimal?","answer":"0.4"}],
  [{"q":1,"topic":"Place Value","question":"What is 100 less than 4,100?","answer":"4,000"},
   {"q":2,"topic":"Multiplication and Division","question":"What is 45 \u00f7 9?","answer":"5"},
   {"q":3,"topic":"Geometry","question":"How many lines of symmetry does an equilateral triangle have?","answer":"3"},
   {"q":4,"topic":"Measurement","question":"A train takes 2 hours 45 minutes and arrives at 5:15 pm.\nWhat time did it set off?","answer":"2:30 pm"},
   {"q":5,"topic":"Addition and Subtraction","question":"Calculate 4,065 + 3,847.","answer":"7,912"}],
  [{"q":1,"topic":"Place Value","question":"Write 2,050 in words.","answer":"two thousand and fifty"},
   {"q":2,"topic":"Addition and Subtraction","question":"Calculate 6,250 \u2212 2,843.","answer":"3,407"},
   {"q":3,"topic":"Fractions and Decimals","question":"How many quarters make 1 whole?","answer":"4 quarters"},
   {"q":4,"topic":"Geometry","question":"What 3D shape is this?","answer":"Cuboid","shape":"cuboid"},
   {"q":5,"topic":"Geometry","question":"A rectangle is 12 cm long and 5 cm wide.\nWhat is its area?","answer":"60 cm\u00b2"}],
  [{"q":1,"topic":"Place Value","question":"Round 6,782 to the nearest 10.","answer":"6,780"},
   {"q":2,"topic":"Multiplication and Division","question":"A farmer has 9 fields with 11 cows in each.\nHow many cows altogether?","answer":"99 cows"},
   {"q":3,"topic":"Geometry","question":"What does 'quadrilateral' mean?","answer":"A 4-sided polygon"},
   {"q":4,"topic":"Addition and Subtraction","question":"Calculate 5,374 + 2,918.","answer":"8,292"},
   {"q":5,"topic":"Measurement","question":"How many millilitres are in 3.5 litres?","answer":"3,500 ml"}],
],

}

# ── Run ────────────────────────────────────────────────────────

if __name__ == "__main__":
    if not os.path.exists(TEMPLATE_FILE):
        print(f"ERROR: {TEMPLATE_FILE} not found."); exit()

    print("Drawing shapes (this takes a moment)...")
    shape_cache = {}
    for week_days in WEEKS.values():
        for qs in week_days:
            for q in qs:
                if "shape" in q and q["shape"] not in shape_cache:
                    fn = SHAPES.get(q["shape"])
                    if fn: print(f"  {q['shape']}"); shape_cache[q["shape"]] = fn()

    print("\nBuilding files...")
    for week_name, days in WEEKS.items():
        build(TEMPLATE_FILE, f"Rapid_Maths_{week_name}.pptx", days, shape_cache)

    print("\nAll done.")
