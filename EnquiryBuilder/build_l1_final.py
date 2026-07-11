#!/usr/bin/env python3
"""T6W7 L1 States of Matter — definitive build."""

import os, sys, shutil, zipfile, re, glob, subprocess
from pathlib import Path
from lxml import etree
from PIL import Image as PILImage

TEMPLATES = Path('/home/claude/enquiry-builder/templates')
SCI_EX    = TEMPLATES / 'sci_example.pptx'
SCI_TPL   = TEMPLATES / 'sci_template.pptx'
KQ_LO     = TEMPLATES / 'KQ_LO.pptx'
MISS      = Path('/mnt/user-data/uploads/missing-sci.pptx')
IMG       = Path('/home/claude/l1_images')
WORK      = Path('/tmp/build_l1')
OUT       = Path('/mnt/user-data/outputs/T6W7 - 1 - Mon - States of Matter L1.pptx')

A=   'http://schemas.openxmlformats.org/drawingml/2006/main'
P=   'http://schemas.openxmlformats.org/presentationml/2006/main'
R=   'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
PKG= 'http://schemas.openxmlformats.org/package/2006/relationships'
CT_NS='http://schemas.openxmlformats.org/package/2006/content-types'
SLIDE_CT ='application/vnd.openxmlformats-officedocument.presentationml.slide+xml'
SLIDE_REL=f'{R}/slide'
IMG_REL  =f'{R}/image'
HD_REL   ='http://schemas.microsoft.com/office/2007/relationships/hdphoto'

LAYOUTS={'We do':'slideLayout3.xml','You do Ind':'slideLayout5.xml',
         'We do - Blank':'slideLayout7.xml','I Do - Blank':'slideLayout6.xml',
         'You do Ind - Blank':'slideLayout9.xml'}
SW,SH=12192000,6858000
TITLE_FONT='Twinkl Cursive Looped Light'
LESSON=dict(key_question='Can materials change their state?',
            lo='compare and group materials as solids, liquids or gases using their observable properties',
            tib='I understand how the three states of matter help scientists explain how most substances in the world around us behave',
            isb='creating a sorting table with at least six materials correctly grouped and one written reason for each')

def xp(s): return etree.fromstring(s.encode())
def ex(t): return str(t).replace('&','&amp;').replace('<','&lt;').replace('>','&gt;').replace('"','&quot;')
def xr(p): return etree.parse(str(p))
def xw(t,p): t.write(str(p),xml_declaration=True,encoding='UTF-8',standalone=True)

def unzip(src,dst):
    shutil.rmtree(dst,ignore_errors=True); os.makedirs(dst)
    with zipfile.ZipFile(src) as z: z.extractall(dst)

def rezip(src,dst):
    os.makedirs(Path(dst).parent,exist_ok=True)
    if os.path.exists(dst): os.remove(dst)
    with zipfile.ZipFile(dst,'w',zipfile.ZIP_DEFLATED) as z:
        for root,dirs,files in os.walk(src):
            for f in files:
                full=os.path.join(root,f); z.write(full,os.path.relpath(full,src))

def next_sn(work):
    ex={int(m.group(1)) for f in os.listdir(f'{work}/ppt/slides')
        for m in [re.match(r'slide(\d+)\.xml$',f)] if m}
    n=1
    while n in ex: n+=1
    return n

def next_mn(work):
    md=f'{work}/ppt/media'; os.makedirs(md,exist_ok=True)
    ex=set()
    for f in os.listdir(md):
        m=re.match(r'(?:image|hdphoto)(\d+)',f.split('.')[0])
        if m: ex.add(int(m.group(1)))
    n=1
    while n in ex: n+=1
    return n

# ── Layout name resolver ──────────────────────────────────────────────────
_work_layouts={}

def _build_layout_map(work):
    global _work_layouts; _work_layouts={}
    for lf in glob.glob(f'{work}/ppt/slideLayouts/slideLayout*.xml'):
        t=xr(lf); r=t.getroot()
        cSld=r.find(f'{{{P}}}cSld')
        name=cSld.get('name','') if cSld is not None else ''
        if name: _work_layouts[name]=os.path.basename(lf)

def _src_layout_name(src_dir, layout_filename):
    lp=f'{src_dir}/ppt/slideLayouts/{layout_filename}'
    if not os.path.exists(lp): return None
    t=xr(lp); r=t.getroot()
    cSld=r.find(f'{{{P}}}cSld')
    return cSld.get('name','') if cSld is not None else None

def resolve_layout(src_dir, src_layout_file):
    """Map source layout to the correct layout in the work dir by name."""
    name=_src_layout_name(src_dir,src_layout_file)
    if name and name in _work_layouts: return _work_layouts[name]
    return src_layout_file  # fallback (same filename)

# ── Atomic rId replacement ────────────────────────────────────────────────
def remap_xml(xml, o2n):
    """Replace all r:embed/r:id/r:link rId refs atomically (single regex pass)."""
    def sub(m):
        attr,rid=m.group(1),m.group(2)
        return f'{attr}="{o2n.get(rid,rid)}"'
    return re.sub(r'(r:(?:embed|id|link))="([^"]+)"', sub, xml)

# ── Slide management ──────────────────────────────────────────────────────
def clear_slides(work):
    for f in glob.glob(f'{work}/ppt/slides/slide*.xml'): os.remove(f)
    for f in glob.glob(f'{work}/ppt/slides/_rels/slide*.xml.rels'): os.remove(f)
    for f in glob.glob(f'{work}/ppt/notesSlides/notesSlide*.xml'): os.remove(f)
    for f in glob.glob(f'{work}/ppt/notesSlides/_rels/notesSlide*.xml.rels'): os.remove(f)
    # Keep media referenced by layouts; remove the rest
    layout_media=set()
    for lf in glob.glob(f'{work}/ppt/slideLayouts/_rels/slideLayout*.xml.rels'):
        t=xr(lf)
        for rel in t.getroot():
            tgt=rel.get('Target','')
            if '../media/' in tgt: layout_media.add(tgt.split('/')[-1])
    for f in glob.glob(f'{work}/ppt/media/*'):
        if os.path.basename(f) not in layout_media: os.remove(f)
    t=xr(f'{work}/ppt/presentation.xml'); r=t.getroot()
    lst=r.find(f'{{{P}}}sldIdLst')
    if lst is not None:
        for c in list(lst): lst.remove(c)
    xw(t,f'{work}/ppt/presentation.xml')
    t=xr(f'{work}/ppt/_rels/presentation.xml.rels'); r=t.getroot()
    for rel in list(r):
        typ=rel.get('Type','')
        if 'slide' in typ.lower() and 'Layout' not in typ and 'Master' not in typ: r.remove(rel)
    xw(t,f'{work}/ppt/_rels/presentation.xml.rels')
    t=xr(f'{work}/[Content_Types].xml'); r=t.getroot()
    for el in list(r):
        pn=el.get('PartName',''); ct=el.get('ContentType','')
        if ct==SLIDE_CT or 'notesSlide' in pn: r.remove(el)
    xw(t,f'{work}/[Content_Types].xml')

def reg_slide(work,sn):
    prels=f'{work}/ppt/_rels/presentation.xml.rels'
    t=xr(prels); r=t.getroot()
    ex={int(m.group(1)) for el in r for m in [re.match(r'rId(\d+)',el.get('Id',''))] if m}
    rid_n=max(ex,default=0)+1; new_rid=f'rId{rid_n}'
    etree.SubElement(r,'Relationship',{'Id':new_rid,'Type':SLIDE_REL,'Target':f'slides/slide{sn}.xml'})
    xw(t,prels)
    pres=f'{work}/ppt/presentation.xml'; t=xr(pres); r=t.getroot()
    lst=r.find(f'{{{P}}}sldIdLst')
    if lst is None: lst=etree.SubElement(r,f'{{{P}}}sldIdLst')
    ex_ids={int(el.get('id',256)) for el in lst}
    new_id=max(ex_ids,default=255)+1
    etree.SubElement(lst,f'{{{P}}}sldId',{'id':str(new_id),f'{{{R}}}id':new_rid})
    xw(t,pres)
    t=xr(f'{work}/[Content_Types].xml'); r=t.getroot()
    pname=f'/ppt/slides/slide{sn}.xml'
    if not any(el.get('PartName')==pname for el in r):
        etree.SubElement(r,f'{{{CT_NS}}}Override',{'PartName':pname,'ContentType':SLIDE_CT})
    xw(t,f'{work}/[Content_Types].xml')

# ── Source cache ──────────────────────────────────────────────────────────
_cache={}
def src_dir(pptx):
    k=str(pptx)
    if k not in _cache:
        dst=f'/tmp/src_{Path(pptx).stem}'; unzip(pptx,dst); _cache[k]=dst
    return _cache[k]

# ── Clone (with atomic rId remap and name-based layout resolution) ─────────
def clone(work, pptx, sn, copy_hdphoto=True):
    sd=src_dir(pptx)
    slide_path=f'{sd}/ppt/slides/slide{sn}.xml'
    rels_path =f'{sd}/ppt/slides/_rels/slide{sn}.xml.rels'
    with open(slide_path,encoding='utf-8') as f: slide_xml=f.read()
    rt=xr(rels_path); rr=rt.getroot()
    md=Path(work)/'ppt'/'media'; md.mkdir(exist_ok=True)
    os.makedirs(f'{work}/ppt/diagrams',exist_ok=True)
    os.makedirs(f'{work}/ppt/notesSlides/_rels',exist_ok=True)
    new_sn=next_sn(work); o2n={}; entries=[]; rn=1

    for rel in rr:
        typ=rel.get('Type',''); tgt=rel.get('Target',''); oid=rel.get('Id','')
        if f'{R}/slideLayout' in typ:
            lf=tgt.split('/')[-1]
            resolved=resolve_layout(sd,lf)
            entries.append((f'rId{rn}',typ,f'../slideLayouts/{resolved}'))
            o2n[oid]=f'rId{rn}'; rn+=1
        elif f'{R}/image' in typ or (HD_REL in typ and copy_hdphoto):
            for c in [f'{sd}/ppt/slides/{tgt}',f'{sd}/ppt/{tgt.lstrip("../")}']:
                if os.path.exists(c):
                    ext=Path(c).suffix.lower(); n=next_mn(work)
                    pfx='hdphoto' if ext=='.wdp' else 'image'
                    nm=f'{pfx}{n}{ext}'; shutil.copy(c,md/nm)
                    entries.append((f'rId{rn}',typ,f'../media/{nm}'))
                    o2n[oid]=f'rId{rn}'; rn+=1; break
        elif any(dt in typ for dt in ['diagramData','diagramLayout','diagramColors','diagramQuickStyle','diagramDrawing']):
            for c in [f'{sd}/ppt/slides/{tgt}',f'{sd}/ppt/{tgt.lstrip("../")}']:
                if os.path.exists(c):
                    orig=Path(c).name; dst=f'{work}/ppt/diagrams/{orig}'
                    if not os.path.exists(dst): shutil.copy(c,dst)
                    ct=xr(f'{work}/[Content_Types].xml'); cr=ct.getroot()
                    pn=f'/ppt/diagrams/{orig}'
                    if not any(el.get('PartName')==pn for el in cr):
                        cm={'data':'diagramData+xml','layout':'diagramLayout+xml','colors':'diagramColors+xml',
                            'quickStyle':'diagramStyle+xml','drawing':'diagramDrawing+xml'}
                        sfx=next((v for k,v in cm.items() if k in orig),'xml')
                        base='application/vnd.openxmlformats-officedocument.drawingml.'
                        etree.SubElement(cr,f'{{{CT_NS}}}Override',{'PartName':pn,'ContentType':base+sfx})
                    xw(ct,f'{work}/[Content_Types].xml')
                    entries.append((f'rId{rn}',typ,f'../diagrams/{orig}'))
                    o2n[oid]=f'rId{rn}'; rn+=1; break
        elif f'{R}/notesSlide' in typ:
            for c in [f'{sd}/ppt/slides/{tgt}',f'{sd}/ppt/{tgt.lstrip("../")}']:
                if os.path.exists(c):
                    nn=f'notesSlide{new_sn}.xml'
                    shutil.copy(c,f'{work}/ppt/notesSlides/{nn}')
                    nr=f'''<?xml version='1.0' encoding='UTF-8' standalone='yes'?>\n<Relationships xmlns="{PKG}">\n  <Relationship Id="rId1" Type="{R}/slide" Target="../slides/slide{new_sn}.xml"/>\n  <Relationship Id="rId2" Type="{R}/notesMaster" Target="../notesMasters/notesMaster1.xml"/>\n</Relationships>'''
                    with open(f'{work}/ppt/notesSlides/_rels/{nn}.rels','w') as f2: f2.write(nr)
                    ct=xr(f'{work}/[Content_Types].xml'); cr=ct.getroot()
                    pn=f'/ppt/notesSlides/{nn}'
                    ns_ct='application/vnd.openxmlformats-officedocument.presentationml.notesSlide+xml'
                    if not any(el.get('PartName')==pn for el in cr):
                        etree.SubElement(cr,f'{{{CT_NS}}}Override',{'PartName':pn,'ContentType':ns_ct})
                    xw(ct,f'{work}/[Content_Types].xml')
                    entries.append((f'rId{rn}',typ,f'../notesSlides/{nn}'))
                    o2n[oid]=f'rId{rn}'; rn+=1; break

    rels_xml=f"<?xml version='1.0' encoding='UTF-8' standalone='yes'?>\n<Relationships xmlns=\"{PKG}\">"
    for rid,typ2,tgt2 in entries:
        rels_xml+=f'\n  <Relationship Id="{rid}" Type="{typ2}" Target="{tgt2}"/>'
    rels_xml+='\n</Relationships>'

    # ATOMIC rId replacement — single regex pass, no cascading corruption
    slide_xml=remap_xml(slide_xml,o2n)

    sp=f'{work}/ppt/slides/slide{new_sn}.xml'
    rp=f'{work}/ppt/slides/_rels/slide{new_sn}.xml.rels'
    os.makedirs(f'{work}/ppt/slides/_rels',exist_ok=True)
    with open(sp,'w',encoding='utf-8') as f: f.write(slide_xml)
    with open(rp,'w',encoding='utf-8') as f: f.write(rels_xml)
    reg_slide(work,new_sn)
    print(f"    slide{new_sn} ← {Path(pptx).stem}:slide{sn} ({len(entries)} rels, layout='{_src_layout_name(sd, [e for e in entries if 'slideLayout' in e[2]][0][2].split('/')[-1]) if any('slideLayout' in e[2] for e in entries) else '?'}'→'{resolve_layout(sd, [r for r in rr if f'{R}/slideLayout' in r.get('Type','')][0].get('Target','').split('/')[-1]) if any(f'{R}/slideLayout' in r.get('Type','') for r in rr) else '?'}')")
    return sp,rp

def fresh(work,layout_name):
    lf=LAYOUTS[layout_name]; sn=next_sn(work)
    slide=f'''<?xml version='1.0' encoding='UTF-8' standalone='yes'?>\n<p:sld xmlns:p="{P}" xmlns:a="{A}" xmlns:r="{R}">\n  <p:cSld><p:spTree>\n    <p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>\n    <p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>\n  </p:spTree></p:cSld>\n  <p:clrMapOvr><a:masterClr/></p:clrMapOvr>\n</p:sld>'''
    rels=f"<?xml version='1.0' encoding='UTF-8' standalone='yes'?>\n<Relationships xmlns=\"{PKG}\">\n  <Relationship Id=\"rId1\" Type=\"{R}/slideLayout\" Target=\"../slideLayouts/{lf}\"/>\n</Relationships>"
    sp=f'{work}/ppt/slides/slide{sn}.xml'; rp=f'{work}/ppt/slides/_rels/slide{sn}.xml.rels'
    os.makedirs(f'{work}/ppt/slides/_rels',exist_ok=True)
    with open(sp,'w',encoding='utf-8') as f: f.write(slide)
    with open(rp,'w',encoding='utf-8') as f: f.write(rels)
    reg_slide(work,sn); print(f"    slide{sn} ← {layout_name}")
    return sp,rp

def get_spTree(sp): t=xr(sp); st=t.getroot().find(f'.//{{{P}}}spTree'); return t,st
def save(t,sp): xw(t,sp)

def title_sp(sid,text,bold=False):
    b=' b="1"' if bold else ''
    return xp(f'<p:sp xmlns:p="{P}" xmlns:a="{A}"><p:nvSpPr><p:cNvPr id="{sid}" name="Title {sid}"/><p:cNvSpPr><a:spLocks noGrp="1"/></p:cNvSpPr><p:nvPr><p:ph type="title"/></p:nvPr></p:nvSpPr><p:spPr/><p:txBody><a:bodyPr/><a:lstStyle/><a:p><a:r><a:rPr lang="en-GB"{b} dirty="0"><a:latin typeface="{TITLE_FONT}" panose="02000000000000000000" pitchFamily="2" charset="77"/></a:rPr><a:t>{ex(text)}</a:t></a:r></a:p></p:txBody></p:sp>')

def body_sp(sid,bullets,sz=2200):
    paras=''.join(f'<a:p><a:r><a:rPr lang="en-GB" sz="{sz}" dirty="0"/><a:t>{ex(b)}</a:t></a:r></a:p>' for b in bullets)
    return xp(f'<p:sp xmlns:p="{P}" xmlns:a="{A}"><p:nvSpPr><p:cNvPr id="{sid}" name="Content Placeholder {sid}"/><p:cNvSpPr><a:spLocks noGrp="1"/></p:cNvSpPr><p:nvPr><p:ph idx="1"/></p:nvPr></p:nvSpPr><p:spPr/><p:txBody><a:bodyPr/><a:lstStyle/>{paras}</p:txBody></p:sp>')

def tbox(sid,text,x,y,cx,cy,sz=1800,bold=False,color='1A3A5C',align='l'):
    b=' b="1"' if bold else ''
    return xp(f'<p:sp xmlns:p="{P}" xmlns:a="{A}"><p:nvSpPr><p:cNvPr id="{sid}" name="TextBox {sid}"/><p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr><p:spPr><a:xfrm><a:off x="{x}" y="{y}"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:noFill/></p:spPr><p:txBody><a:bodyPr wrap="square" autofit="normAutofit"/><a:lstStyle/><a:p><a:pPr algn="{align}"/><a:r><a:rPr lang="en-GB" sz="{sz}"{b} dirty="0"><a:solidFill><a:srgbClr val="{color}"/></a:solidFill></a:rPr><a:t>{ex(text)}</a:t></a:r></a:p></p:txBody></p:sp>')

def add_img(sp,rp,work,img_path,x,y,mw,mh,sid):
    img=PILImage.open(img_path); iw,ih=img.size
    sc=min(mw/iw,mh/ih); w=int(iw*sc); h=int(ih*sc)
    cx=x+(mw-w)//2; cy=y+(mh-h)//2
    n=next_mn(work); ext=Path(img_path).suffix.lower(); nm=f'image{n}{ext}'
    md=Path(work)/'ppt'/'media'; md.mkdir(exist_ok=True); shutil.copy(img_path,md/nm)
    rt=xr(rp); rr=rt.getroot()
    ex_rids={int(m.group(1)) for el in rr for m in [re.match(r'rId(\d+)',el.get('Id',''))] if m}
    rn=max(ex_rids,default=0)+1; rid=f'rId{rn}'
    etree.SubElement(rr,'Relationship',{'Id':rid,'Type':IMG_REL,'Target':f'../media/{nm}'})
    rt.write(rp,xml_declaration=True,encoding='UTF-8',standalone=True)
    st=xr(sp); spTree=st.getroot().find(f'.//{{{P}}}spTree')
    spTree.append(xp(f'<p:pic xmlns:p="{P}" xmlns:a="{A}" xmlns:r="{R}"><p:nvPicPr><p:cNvPr id="{sid}" name="Picture {sid}"/><p:cNvPicPr><a:picLocks noChangeAspect="1"/></p:cNvPicPr><p:nvPr/></p:nvPicPr><p:blipFill><a:blip r:embed="{rid}"/><a:stretch><a:fillRect/></a:stretch></p:blipFill><p:spPr><a:xfrm><a:off x="{cx}" y="{cy}"/><a:ext cx="{w}" cy="{h}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></p:spPr></p:pic>'))
    st.write(sp,xml_declaration=True,encoding='UTF-8',standalone=True)

def anim_body(sp,sid,n):
    st=xr(sp); root=st.getroot()
    for el in list(root):
        if el.tag==f'{{{P}}}timing': root.remove(el)
    c=3
    hide=f'<p:par><p:cTn id="{c}" fill="hold"><p:stCondLst><p:cond delay="0"/></p:stCondLst><p:childTnLst><p:set><p:cBhvr><p:cTn id="{c+1}" dur="1" fill="hold"/><p:tgtEl><p:spTgt spid="{sid}"/></p:tgtEl><p:attrNameLst><p:attrName>style.visibility</p:attrName></p:attrNameLst></p:cBhvr><p:to><p:strVal val="hidden"/></p:to></p:set></p:childTnLst></p:cTn></p:par>'; c+=2
    seq=''
    for i in range(n):
        c1,c2,c3=c,c+1,c+2
        seq+=f'<p:par><p:cTn id="{c1}" fill="hold"><p:stCondLst><p:cond evt="onBegin" delay="indefinite"/></p:stCondLst><p:childTnLst><p:par><p:cTn id="{c2}" presetID="1" presetClass="entr" presetSubtype="0" fill="hold" grpId="{i}" nodeType="clickEffect"><p:stCondLst><p:cond delay="0"/></p:stCondLst><p:childTnLst><p:set><p:cBhvr><p:cTn id="{c3}" dur="1" fill="hold"/><p:tgtEl><p:spTgt spid="{sid}"><p:txEl><p:pRg st="{i}" end="{i}"/></p:txEl></p:spTgt></p:tgtEl><p:attrNameLst><p:attrName>style.visibility</p:attrName></p:attrNameLst></p:cBhvr><p:to><p:strVal val="visible"/></p:to></p:set></p:childTnLst></p:cTn></p:par></p:childTnLst></p:cTn></p:par>'; c=c3+1
    bld=f'<p:bldLst xmlns:p="{P}"><p:bldP spid="{sid}" grpId="0" build="p"/></p:bldLst>'
    timing=f'<p:timing xmlns:p="{P}"><p:tnLst><p:par><p:cTn id="1" dur="indefinite" restart="whenNotActive" nodeType="tmRoot"><p:childTnLst>{hide}<p:seq concurrent="1" nextAc="seek"><p:cTn id="2" dur="indefinite" nodeType="mainSeq"><p:childTnLst>{seq}</p:childTnLst></p:cTn><p:prevCondLst><p:cond evt="onPrevClick" delay="0"/></p:prevCondLst><p:nextCondLst><p:cond evt="onNextClick" delay="0"/></p:nextCondLst></p:seq></p:childTnLst></p:cTn></p:par></p:tnLst>{bld}</p:timing>'
    root.append(xp(timing)); xw(st,sp)

def anim_shapes(sp,groups):
    st=xr(sp); root=st.getroot()
    for el in list(root):
        if el.tag==f'{{{P}}}timing': root.remove(el)
    all_ids=[i for g in groups for i in g]; c=3; hide=''
    for sid in all_ids:
        hide+=f'<p:par><p:cTn id="{c}" fill="hold"><p:stCondLst><p:cond delay="0"/></p:stCondLst><p:childTnLst><p:set><p:cBhvr><p:cTn id="{c+1}" dur="1" fill="hold"/><p:tgtEl><p:spTgt spid="{sid}"/></p:tgtEl><p:attrNameLst><p:attrName>style.visibility</p:attrName></p:attrNameLst></p:cBhvr><p:to><p:strVal val="hidden"/></p:to></p:set></p:childTnLst></p:cTn></p:par>'; c+=2
    seq=''
    for gi,grp in enumerate(groups):
        inner=''.join(f'<p:par><p:cTn id="{c+j*3}" presetID="1" presetClass="entr" presetSubtype="0" fill="hold" grpId="{gi}" nodeType="clickEffect"><p:stCondLst><p:cond delay="0"/></p:stCondLst><p:childTnLst><p:set><p:cBhvr><p:cTn id="{c+j*3+1}" dur="1" fill="hold"/><p:tgtEl><p:spTgt spid="{sid}"/></p:tgtEl><p:attrNameLst><p:attrName>style.visibility</p:attrName></p:attrNameLst></p:cBhvr><p:to><p:strVal val="visible"/></p:to></p:set></p:childTnLst></p:cTn></p:par>' for j,sid in enumerate(grp))
        oid=c+len(grp)*3
        seq+=f'<p:par><p:cTn id="{oid}" fill="hold"><p:stCondLst><p:cond evt="onBegin" delay="indefinite"/></p:stCondLst><p:childTnLst>{inner}</p:childTnLst></p:cTn></p:par>'; c=oid+1
    timing=f'<p:timing xmlns:p="{P}"><p:tnLst><p:par><p:cTn id="1" dur="indefinite" restart="whenNotActive" nodeType="tmRoot"><p:childTnLst>{hide}<p:seq concurrent="1" nextAc="seek"><p:cTn id="2" dur="indefinite" nodeType="mainSeq"><p:childTnLst>{seq}</p:childTnLst></p:cTn><p:prevCondLst><p:cond evt="onPrevClick" delay="0"/></p:prevCondLst><p:nextCondLst><p:cond evt="onNextClick" delay="0"/></p:nextCondLst></p:seq></p:childTnLst></p:cTn></p:par></p:tnLst></p:timing>'
    root.append(xp(timing)); xw(st,sp)

def find_sp(tree,name):
    for s in tree.iter(f'{{{P}}}sp'):
        for el in s.iter():
            if el.get('name')==name: return s
    return None

def get_sp_id(tree,name):
    s=find_sp(tree,name)
    if s is None: return None
    c=s.find(f'.//{{{P}}}cNvPr'); return int(c.get('id',0)) if c is not None else None

def set_text(s,text):
    tb=None
    for ns in [P,A]:
        tb=s.find(f'.//{{{ns}}}txBody')
        if tb is not None: break
    if tb is None: return
    paras=tb.findall(f'{{{A}}}p')
    if not paras: return
    fp=paras[0]; runs=fp.findall(f'{{{A}}}r')
    rpr=runs[0].find(f'{{{A}}}rPr') if runs else None
    for r in list(fp.findall(f'{{{A}}}r')): fp.remove(r)
    for br in list(fp.findall(f'{{{A}}}br')): fp.remove(br)
    for pp in paras[1:]: tb.remove(pp)
    for i,line in enumerate(text.split('\n')):
        p=fp if i==0 else etree.SubElement(tb,f'{{{A}}}p')
        if i>0 and rpr is not None:
            pp2=fp.find(f'{{{A}}}pPr')
            if pp2 is not None: p.append(etree.fromstring(etree.tostring(pp2)))
        nr=etree.SubElement(p,f'{{{A}}}r')
        if rpr is not None: nr.append(etree.fromstring(etree.tostring(rpr)))
        t=etree.SubElement(nr,f'{{{A}}}t'); t.text=line

# ── Slide builders ────────────────────────────────────────────────────────
def build_cover(work):
    print("  [7] Cover")
    sp,rp=clone(work,SCI_TPL,2,copy_hdphoto=True)
    tree=xr(sp)
    for s in list(tree.iter(f'{{{P}}}sp')):
        for el in s.iter():
            if el.get('name')=='TextBox 19': s.getparent().remove(s); break
    kq=find_sp(tree,'TextBox 16')
    if kq is not None: set_text(kq,LESSON['key_question'])
    ch=find_sp(tree,'TextBox 17')
    if ch is not None:
        tb=None
        for ns in [P,A]:
            tb=ch.find(f'.//{{{ns}}}txBody')
            if tb is not None: break
        if tb is not None:
            for pp in list(tb.findall(f'{{{A}}}p')): tb.remove(pp)
            etree.SubElement(tb,f'{{{A}}}p')
    xw(tree,sp)

def build_lo(work):
    print("  [8] LO")
    sp,rp=clone(work,KQ_LO,1,copy_hdphoto=True)
    tree=xr(sp)
    for name,val in [('Title 27',LESSON['key_question']),('TextBox 38',LESSON['lo']),
                     ('TextBox 39',LESSON['tib']),('TextBox 40',LESSON['isb'])]:
        s=find_sp(tree,name)
        if s is not None: set_text(s,val)
    xw(tree,sp)
    tree=xr(sp)
    ids=[get_sp_id(tree,n) for n in ('TextBox 38','TextBox 39','TextBox 40')]
    if all(ids): anim_shapes(sp,[[i] for i in ids])

def build_wedo_hook(work):
    print("  [9] We Do hook")
    sp,rp=fresh(work,'We do')
    t,st=get_spTree(sp)
    st.append(title_sp(2,'What do you already know about materials?'))
    st.append(body_sp(3,['Think about the objects around you \u2014 how would you describe them?',
                          'Which materials can you pour? Which ones keep their shape?',
                          'Do you know what the words solid, liquid and gas mean?']))
    save(t,sp); anim_body(sp,3,3)

def build_grid(work):
    print("  [10] We Do image grid")
    sp,rp=fresh(work,'We do - Blank')
    t,st=get_spTree(sp); st.append(title_sp(2,'Sort these \u2014 solid, liquid or gas?')); save(t,sp)
    MX,MY=150000,1750000; TW=SW-2*MX; TH=SH-MY-80000
    CW=TW//4; CH=TH//2; LH=400000; IH=CH-LH-60000; IW=CW-80000
    items=[('Ice','grid/ice.png'),('Water','grid/water.png'),('Steam\n(water vapour)','grid/steam_water_vapour.png'),
           ('Wood','grid/wood.png'),('Sand','grid/sand.png'),('Milk','grid/milk.png'),
           ('Balloon\n(filled with air)','grid/balloon_air_inside.png'),('Honey','grid/honey.png')]
    sid=10
    for i,(lbl,img) in enumerate(items):
        row,col=divmod(i,4); cx=MX+col*CW; cy=MY+row*CH; ip=IMG/img
        if ip.exists(): add_img(sp,rp,work,str(ip),cx+40000,cy+20000,IW,IH,sid); sid+=1
        t2,st2=get_spTree(sp); st2.append(tbox(sid,lbl,cx,cy+IH+40000,CW,LH,sz=1600,bold=True,color='1A3A5C',align='ctr')); save(t2,sp); sid+=1

def build_ido(work):
    print("  [11] I Do particle")
    sp,rp=fresh(work,'I Do - Blank')
    t,st=get_spTree(sp); st.append(title_sp(2,'How are the particles arranged?',bold=True)); save(t,sp)
    add_img(sp,rp,work,str(IMG/'particle_model.png'),5400000,1600000,6500000,4800000,3)
    bullets=[('In a SOLID,','particles are packed tightly in a fixed arrangement\u2014the solid keeps its shape.'),
             ('In a LIQUID,','particles are close but can slide past each other\u2014the liquid flows and takes the shape of its container.'),
             ('In a GAS,','particles move quickly and are spread far apart\u2014the gas fills the entire space available.')]
    sid=10; groups=[]
    for i,(lbl,desc) in enumerate(bullets):
        by=1550000+i*1540000
        t2,st2=get_spTree(sp); st2.append(tbox(sid,lbl,180000,by,5000000,550000,sz=2000,bold=True,color='1A5276',align='l')); save(t2,sp); l_id=sid; sid+=1
        t2,st2=get_spTree(sp); st2.append(tbox(sid,desc,180000,by+500000,5000000,1000000,sz=1800,color='1A3A5C',align='l')); save(t2,sp); d_id=sid; sid+=1
        groups.append([l_id,d_id])
    anim_shapes(sp,groups)

def build_discussion(work):
    print("  [12] You Do discussion")
    sp,rp=fresh(work,'You do Ind - Blank')
    t,st=get_spTree(sp); st.append(title_sp(2,'Is this a solid or a liquid?')); save(t,sp)
    add_img(sp,rp,work,str(IMG/'oobleck_placeholder.png'),838200,1700000,10515600,4900000,3)

def build_youdo(work):
    print("  [13] You Do task")
    sp,rp=fresh(work,'You do Ind')
    t,st=get_spTree(sp)
    st.append(title_sp(2,'Sort the materials'))
    st.append(body_sp(3,['Sort the material cards into three groups: solid, liquid or gas',
                          'Record your decisions in the table on your LP',
                          'For each material, write one reason \u2014 use the particle model to help you',
                          'Challenge: can you find one material that is difficult to classify? Why?']))
    save(t,sp); anim_body(sp,3,4)

def build_review(work):
    print("  [14] Learning review")
    sp,rp=clone(work,SCI_EX,17,copy_hdphoto=True)
    tree=xr(sp)
    starters=['I can now explain the difference between a solid, liquid and gas because\u2026',
              'Something that surprised me was\u2026','I am still wondering\u2026']
    bmap={'Bubble1':0,'Bubble2':1,'Bubble3':2}
    for s in tree.iter(f'{{{P}}}sp'):
        for el in s.iter():
            nm=el.get('name','')
            if nm in bmap: set_text(s,starters[bmap[nm]]); break
    xw(tree,sp)

# ── MAIN ─────────────────────────────────────────────────────────────────
if __name__=='__main__':
    print("Setting up...")
    unzip(SCI_EX,WORK); clear_slides(WORK)
    _build_layout_map(WORK)
    print(f"Work layout map: { {k:v for k,v in _work_layouts.items() if k in ['Title Slide','Blank','Title and Content','I do','We do','You do Ind']} }")

    src_dir(SCI_TPL); src_dir(KQ_LO); src_dir(SCI_EX); src_dir(MISS)

    print("\n6 missing-sci slides:")
    for n in range(1,7): clone(WORK,MISS,n,copy_hdphoto=True)

    print("\n8 lesson slides:")
    build_cover(WORK); build_lo(WORK); build_wedo_hook(WORK)
    build_grid(WORK); build_ido(WORK); build_discussion(WORK)
    build_youdo(WORK); build_review(WORK)

    r=subprocess.run(['python3','/mnt/skills/public/pptx/scripts/clean.py',str(WORK)],
                     capture_output=True,text=True)
    if r.stdout.strip(): print(f"\nClean: {r.stdout.strip()[:200]}")

    rezip(str(WORK),str(OUT))
    print(f"\n\u2192 {OUT.name} ({OUT.stat().st_size:,} bytes)")
