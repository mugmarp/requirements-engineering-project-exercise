#!/usr/bin/env python3
"""
Reusable DOCX builder for the Deniz Construction (DCMS) SWE2102 project.

Format standard (fixed for all project documents):
  Font          Times New Roman
  Size          12 pt
  Colour        black
  Line spacing  1.15
  Bold          applied only where necessary (headings, table headers, key terms)
  Punctuation   plain ASCII. No curly quotes, no semicolons, no en/em dashes.

Usage:
  python3 build_docx.py spec.json out.docx

Spec format (JSON):
  {
    "title": "...",
    "meta":   [ "line one", "line two" ],
    "blocks": [
      {"type": "h1" | "h2" | "h3", "text": "..."},
      {"type": "para", "text": "..."},
      {"type": "para", "runs": [{"text": "...", "bold": true}, {"text": "..."}]},
      {"type": "bullets", "items": ["...", "..."]},
      {"type": "numbered", "items": ["...", "..."]},
      {"type": "table", "header": ["A","B"], "rows": [["1","2"]]},
      {"type": "pagebreak"}
    ]
  }
"""

import json
import re
import sys

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml.ns import qn
from docx.shared import Pt, RGBColor

FONT_NAME = "Times New Roman"
FONT_SIZE = Pt(12)
FONT_COLOUR = RGBColor(0, 0, 0)
LINE_SPACING = 1.15

# Punctuation normalisation. Curly quotes, semicolons, en/em dashes and
# horizontal bars are flattened to plain ASCII so the document carries no
# typographic decoration.
PUNCT_MAP = {
    "\u201c": "'",  # left double quote
    "\u201d": "'",  # right double quote
    "\u2018": "'",  # left single quote
    "\u2019": "'",  # right single quote
    "\u201a": ",",
    "\u201e": ",",
    "\u2013": "-",  # en dash
    "\u2014": "-",  # em dash
    "\u2212": "-",  # minus sign
    "\u00a0": " ",  # non breaking space
}


def fix_case(text):
    """Capitalise the letter after a sentence break introduced by substitution."""
    return re.sub(r"\. ([a-z])", lambda m: ". " + m.group(1).upper(), text)


def clean(text: str) -> str:
    """Flatten punctuation and collapse whitespace runs.

    The project format standard bans decorative punctuation: straight and curly
    quotes, semicolons, hyphens and dashes. Possessives and contractions are
    expanded rather than dropped so no word is mangled.
    """
    if not isinstance(text, str):
        return text
    for src, dst in PUNCT_MAP.items():
        text = text.replace(src, dst)
    # semicolon becomes a sentence break
    text = text.replace("; ", ". ")
    text = text.replace(";", ".")
    # expand contractions before dropping the apostrophe
    text = text.replace("n't", " not")
    # drop possessive 's
    text = text.replace("'s ", " ")
    text = text.replace("'s,", ",")
    text = text.replace("'s.", ".")
    # remove remaining quotes and apostrophes
    text = text.replace('"', "")
    text = text.replace("'", "")
    # hyphens become spaces so End-of-Day reads End of Day, not EndofDay
    text = text.replace("-", " ")
    text = fix_case(text)
    # collapse doubled spaces introduced by substitutions, but keep a single
    # trailing space so bold lead in runs stay separated from the body text
    text = re.sub(r"[ \t]{2,}", " ", text)
    return text


def set_run(run, bold=False):
    run.font.name = FONT_NAME
    run.font.size = FONT_SIZE
    run.font.color.rgb = FONT_COLOUR
    run.font.bold = bold
    # ensure the east-asian / complex-script font slots also use Times
    rpr = run._element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = rpr.makeelement(qn("w:rFonts"), {})
        rpr.append(rfonts)
    for attr in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
        rfonts.set(qn(attr), FONT_NAME)


def style_paragraph(p, space_before=0, space_after=6, align=None):
    pf = p.paragraph_format
    pf.line_spacing_rule = WD_LINE_SPACING.MULTIPLE
    pf.line_spacing = LINE_SPACING
    pf.space_before = Pt(space_before)
    pf.space_after = Pt(space_after)
    if align is not None:
        p.alignment = align


def add_title(doc, text):
    p = doc.add_paragraph()
    style_paragraph(p, space_after=4, align=WD_ALIGN_PARAGRAPH.CENTER)
    set_run(p.add_run(clean(text)), bold=True)
    return p


def add_meta(doc, lines):
    for line in lines:
        p = doc.add_paragraph()
        style_paragraph(p, space_after=2, align=WD_ALIGN_PARAGRAPH.CENTER)
        set_run(p.add_run(clean(line)), bold=False)
    # thin spacer after the meta block
    spacer = doc.add_paragraph()
    style_paragraph(spacer, space_after=10)
    spacer.add_run("")


def add_heading(doc, text, level):
    p = doc.add_paragraph()
    style_paragraph(p, space_before=12, space_after=6)
    set_run(p.add_run(clean(text)), bold=True)
    return p


def add_para(doc, text=None, runs=None):
    p = doc.add_paragraph()
    style_paragraph(p, space_after=6)
    if runs:
        for spec in runs:
            set_run(p.add_run(clean(spec["text"])), bold=bool(spec.get("bold")))
    else:
        set_run(p.add_run(clean(text)), bold=False)
    return p


def add_list(doc, items, numbered=False):
    for item in items:
        p = doc.add_paragraph()
        style_paragraph(p, space_after=3)
        marker = "%d.  " % (len(doc.paragraphs),) if False else ""
        # manual numbering keeps control over the marker text
        if numbered:
            idx = getattr(add_list, "_counter", 0) + 1
            add_list._counter = idx
            marker = "%d.  " % idx
        else:
            marker = "\u2022  "
        set_run(p.add_run(marker), bold=False)
        set_run(p.add_run(clean(item)), bold=False)


def reset_counters():
    add_list._counter = 0


def add_table(doc, header, rows):
    ncols = len(header)
    table = doc.add_table(rows=1, cols=ncols)
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER

    hdr = table.rows[0].cells
    for i, cell_text in enumerate(header):
        cell = hdr[i]
        cell.text = ""
        p = cell.paragraphs[0]
        style_paragraph(p, space_before=2, space_after=2)
        set_run(p.add_run(clean(cell_text)), bold=True)

    for row in rows:
        cells = table.add_row().cells
        for i in range(ncols):
            value = row[i] if i < len(row) else ""
            cell = cells[i]
            cell.text = ""
            p = cell.paragraphs[0]
            style_paragraph(p, space_before=2, space_after=2)
            set_run(p.add_run(clean(value)), bold=False)

    spacer = doc.add_paragraph()
    style_paragraph(spacer, space_after=8)
    spacer.add_run("")
    return table


def build(spec, out_path):
    doc = Document()

    # page setup: A4 with 25.4 mm margins
    section = doc.sections[0]
    from docx.shared import Mm
    section.page_width = Mm(210)
    section.page_height = Mm(297)
    section.top_margin = Mm(25.4)
    section.bottom_margin = Mm(25.4)
    section.left_margin = Mm(25.4)
    section.right_margin = Mm(25.4)

    # default style so any unstyled paragraph still matches the standard
    normal = doc.styles["Normal"]
    normal.font.name = FONT_NAME
    normal.font.size = FONT_SIZE
    normal.font.color.rgb = FONT_COLOUR
    normal.paragraph_format.line_spacing_rule = WD_LINE_SPACING.MULTIPLE
    normal.paragraph_format.line_spacing = LINE_SPACING

    add_title(doc, spec["title"])
    add_meta(doc, spec.get("meta", []))

    reset_counters()
    for block in spec.get("blocks", []):
        kind = block["type"]
        if kind == "h1":
            add_heading(doc, block["text"], 1)
        elif kind == "h2":
            add_heading(doc, block["text"], 2)
        elif kind == "h3":
            add_heading(doc, block["text"], 3)
        elif kind == "para":
            add_para(doc, text=block.get("text"), runs=block.get("runs"))
        elif kind == "bullets":
            add_list(doc, block["items"], numbered=False)
        elif kind == "numbered":
            reset_counters()
            add_list(doc, block["items"], numbered=True)
        elif kind == "table":
            add_table(doc, block["header"], block["rows"])
        elif kind == "pagebreak":
            doc.add_page_break()
        else:
            raise ValueError("unknown block type: %r" % kind)

    doc.save(out_path)
    return out_path


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        return 1
    with open(sys.argv[1], encoding="utf-8") as fh:
        spec = json.load(fh)
    out = build(spec, sys.argv[2])
    print(json.dumps({"written": out, "blocks": len(spec.get("blocks", []))}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
