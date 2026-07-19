# Science Lesson Builder — Lessons Learned
*Documented after Y5 Astronomy L5 build — July 2026*

---

## 1. NEVER BUILD SLIDES PROGRAMMATICALLY IF A REFERENCE EXISTS

**What went wrong:** Spent days trying to reproduce Innes's hand-crafted slide 1 using `build_kq_challenge()` — tweaking EMU coordinates, fixing phantom shapes, fighting font normalisation. It never matched.

**Rule:** If Innes has a correct version of a slide (uploaded as a .pptx), clone it directly. Do not attempt to reproduce it programmatically. The programmatic builder is for slides that don't yet exist, not for replicating hand-crafted work.

**Implementation:** When a reference slide is provided:
1. Extract slide XML from the uploaded file
2. Rename all media with unique 10-digit suffixes (see Rule 3)
3. Update rels to point to renamed media
4. Replace the target slide XML and rels directly in the deck
5. Never touch the slide XML content — clone it byte-for-byte

---

## 2. MEDIA FILENAME CONFLICTS WILL SILENTLY DESTROY OTHER SLIDES

**What went wrong:** Inserting slide 3 overwrote `image1.png`, `image2.png` etc. in the deck because SLIDE 3.pptx happened to use the same filenames. Slide 1's children images were replaced with slide 3's content. The deck appeared to open fine but slide 1 was visually broken.

**Rule:** When inserting any slide from an external PPTX, **always rename every single media file** from the source before inserting — regardless of whether a conflict exists. Do not check for conflicts and only rename clashes. Rename everything, every time.

**Implementation:**
```python
def rand10():
    return ''.join(random.choices(string.digits, k=10))

for old_path in src_media:
    ext = os.path.splitext(old_path)[1]
    label = re.sub(r'\d+', '', os.path.splitext(os.path.basename(old_path))[0]).strip('_') or 'media'
    rename_map[old_path] = f'ppt/media/{label}_{rand10()}{ext}'
```

Then update the slide's rels file to point to the new names before inserting. Add all renamed media as new files — never overwrite existing ones.

---

## 3. ALWAYS USE presentation.xml FOR SLIDE ORDER, NOT FILENAME SORTING

**What went wrong:** `sorted(['slide1.xml','slide10.xml','slide2.xml'])` returns `['slide1.xml','slide10.xml','slide2.xml']` — slide10 sorts before slide2. Targeting `deck_slides[2]` replaced slide 11, not slide 3.

**Rule:** Always determine slide order from `ppt/presentation.xml` → `ppt/_rels/presentation.xml.rels`. Never use alphabetical sort on filenames to infer slide position.

**Implementation:**
```python
prs = et.fromstring(z.read('ppt/presentation.xml'))
rels = et.fromstring(z.read('ppt/_rels/presentation.xml.rels'))
rid_to_target = {r.get('Id'): r.get('Target') for r in rels}
ordered_slides = [rid_to_target[s.get(f'{{{R}}}id')] for s in prs.find(f'{{{P}}}sldIdLst')]
# ordered_slides[0] = slide 1, ordered_slides[6] = slide 7, etc.
```

---

## 4. BLANKET POST-PROCESSING FIXES BREAK SLIDES THAT ARE ALREADY CORRECT

**What went wrong:** Applied global post-processing (normalising TitleBeing positions, fixing ellipse sizes) to every slide. This destroyed the atom diagram slide which was already correct.

**Rule:** Post-processing must be slide-specific and opt-in. The only safe blanket operation is `_normalise_fonts()`. Everything else must target a named shape on a named slide.

**Pattern:**
```python
# SAFE — blanket
for slide in slides:
    _normalise_fonts(slide)

# SAFE — targeted
if slide_index == 2:  # Being a Scientist slide only
    fix_title_being_position(slide)
```

---

## 5. TEXT-ONLY EDITS: PRESERVE RUN FORMATTING, REPLACE TEXT ONLY

**What worked:** To change text in a cloned slide while keeping fonts/sizes/colours:
1. Collect all `<a:r>` runs across all paragraphs
2. Set the text on the first run's `<a:t>` only
3. Remove all other runs
4. Remove all extra paragraphs

Never replace the paragraph or run element itself — only change the `<a:t>` text node.

---

## 6. DELETING A SLIDE: REMOVE FROM BOTH sldIdLst AND THE RELS FILE

**Rule:** To properly delete slide N:
1. Remove its `<p:sldId>` from `ppt/presentation.xml` → `<p:sldIdLst>`
2. Remove its `<Relationship>` from `ppt/_rels/presentation.xml.rels`
3. Exclude `ppt/slides/slideN.xml` and `ppt/slides/_rels/slideN.xml.rels` from the output zip

Do not just skip writing the slide file — the presentation.xml reference must also be removed or PowerPoint will repair/crash.

---

## 7. IMAGE LAYOUT LOGIC FOR FUTURE SLIDES

When a slide contains an image, the layout choice should be driven by the **purpose** of the image:

### A. Full-bleed / Background
- Image fills the entire slide (or most of it)
- Used for: immersive openers, scene-setting, atmosphere
- Text: overlaid with a semi-transparent box or kept to a minimal banner
- cx/cy: 12192000 × 6858000 (full slide EMUs)

### B. Hero / Split-screen (image left or right, text opposite)
- Image occupies roughly half the slide (left or right column)
- Text occupies the other half
- Used for: introducing a concept with a single strong visual
- Image: cx ≈ 5500000–6000000, full height or near-full
- Text column: starts at x ≈ 6500000, cx ≈ 5500000

### C. Illustration / Supporting (image beside or below body text)
- Image is smaller, secondary to the text
- Used for: labelled diagrams, examples within a longer explanation
- Image: cx ≈ 3000000–4500000, positioned to not crowd the text
- Caption text box directly below or beside image

### D. Diagram / Labelled figure (image centred, labels around it)
- Image is the main content, occupies centre-left or full width
- Labels/callouts are text boxes positioned around the image
- Used for: anatomy diagrams, process flows, maps
- Phases slide layout: large image cx=9035107, right-column text boxes at x=9361172

### E. Icon / Small reference (corner image, decorative/branding)
- Image is small (cx ≈ 400000–800000), positioned top-right or bottom-right
- Used for: subject icons, 21st Century Skills, Being a Scientist icon
- Does not compete with slide content

### Decision logic:
```
Is the image the MAIN content? → D (diagram) or A (full-bleed)
Is the image EQUAL to the text? → B (split-screen)
Is the image SUPPORTING the text? → C (illustration)
Is the image DECORATIVE/BRANDING? → E (icon)
```

---

## 8. WORKFLOW FOR FUTURE LESSON BUILDS

For each new lesson deck:

1. **Check what reference slides Innes has.** If he has a hand-corrected version of any slide, clone it — do not rebuild programmatically.

2. **For slides built programmatically**, use the MTP JSON as the sole content source. Do not hardcode text.

3. **Before inserting any external slide**, rename ALL its media with `_{rand10()}` suffixes. Update rels. Then insert.

4. **After building**, verify slide order using presentation.xml, not filename sort.

5. **Run only `_normalise_fonts()`** as a blanket post-process. Nothing else globally.

6. **For images**, identify purpose first (A–E above), then select layout accordingly.

7. **Do not attempt pixel-perfect positioning via code** for slides Innes will hand-correct anyway. Get close enough, then let Innes adjust and re-upload.

---

## 9. THE BUILDER SCRIPT SHOULD BE UPDATED TO SUPPORT SLIDE CLONING

`build_science_lesson.py` needs a function:

```python
def clone_slide_from_file(src_pptx_path, deck_zip_path, target_slide_number):
    """
    Replaces target_slide_number in deck with slide 1 from src_pptx_path.
    Renames all media from src with unique 10-digit suffixes.
    Uses presentation.xml to identify correct target slide file.
    """
```

This should replace `build_kq_challenge()` for slide 1, and be available for any slide where a reference file exists.

