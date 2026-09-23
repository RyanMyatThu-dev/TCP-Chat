"""Build the TCP Chat learning handbook PDF from the Markdown notes."""

from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "output" / "pdf" / "tcp-chat-learning-handbook.pdf"
SOURCES = [
    ROOT / "learning" / "lessons" / "01-sockets.md",
    ROOT / "learning" / "lessons" / "02-threading.md",
    ROOT / "learning" / "progress" / "knowledge-tree.md",
]

NAVY = colors.HexColor("#17324D")
BLUE = colors.HexColor("#246B9E")
PALE_BLUE = colors.HexColor("#EAF3F8")
INK = colors.HexColor("#24303A")
MUTED = colors.HexColor("#5D6B76")


def make_styles() -> dict[str, ParagraphStyle]:
    sheet = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "TitleCustom", parent=sheet["Title"], fontName="Helvetica-Bold",
            fontSize=25, leading=30, textColor=NAVY, alignment=TA_CENTER,
            spaceAfter=10,
        ),
        "subtitle": ParagraphStyle(
            "Subtitle", parent=sheet["Normal"], fontSize=11, leading=16,
            textColor=MUTED, alignment=TA_CENTER, spaceAfter=18,
        ),
        "h1": ParagraphStyle(
            "H1Custom", parent=sheet["Heading1"], fontName="Helvetica-Bold",
            fontSize=18, leading=22, textColor=NAVY, spaceBefore=10,
            spaceAfter=9,
        ),
        "h2": ParagraphStyle(
            "H2Custom", parent=sheet["Heading2"], fontName="Helvetica-Bold",
            fontSize=13, leading=17, textColor=BLUE, spaceBefore=10,
            spaceAfter=6, keepWithNext=True,
        ),
        "h3": ParagraphStyle(
            "H3Custom", parent=sheet["Heading3"], fontName="Helvetica-Bold",
            fontSize=11, leading=14, textColor=NAVY, spaceBefore=8,
            spaceAfter=4, keepWithNext=True,
        ),
        "body": ParagraphStyle(
            "BodyCustom", parent=sheet["BodyText"], fontName="Helvetica",
            fontSize=9.5, leading=14, textColor=INK, spaceAfter=6,
        ),
        "bullet": ParagraphStyle(
            "BulletCustom", parent=sheet["BodyText"], fontName="Helvetica",
            fontSize=9.3, leading=13, textColor=INK, leftIndent=14,
            firstLineIndent=-7, spaceAfter=3,
        ),
        "code": ParagraphStyle(
            "CodeCustom", parent=sheet["Code"], fontName="Courier",
            fontSize=8, leading=11, textColor=INK, backColor=PALE_BLUE,
            borderColor=colors.HexColor("#C9DCE8"), borderWidth=0.5,
            borderPadding=7, leftIndent=5, rightIndent=5, spaceBefore=4,
            spaceAfter=8,
        ),
    }


def inline_markup(text: str) -> str:
    """Escape text and apply minimal inline-code formatting."""
    pieces = escape(text).split("`")
    return "".join(
        f'<font name="Courier" color="#174E73">{piece}</font>'
        if index % 2 else piece
        for index, piece in enumerate(pieces)
    )


def markdown_story(path: Path, style_map: dict[str, ParagraphStyle]) -> list:
    story: list = []
    paragraph_lines: list[str] = []
    code_lines: list[str] = []
    in_code = False

    def flush_paragraph() -> None:
        if paragraph_lines:
            text = " ".join(line.strip() for line in paragraph_lines)
            story.append(Paragraph(inline_markup(text), style_map["body"]))
            paragraph_lines.clear()

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.rstrip()
        if line.startswith("```"):
            flush_paragraph()
            if in_code:
                code = "<br/>".join(escape(value) or " " for value in code_lines)
                story.append(Paragraph(code, style_map["code"]))
                code_lines.clear()
            in_code = not in_code
            continue
        if in_code:
            code_lines.append(line)
            continue
        if not line:
            flush_paragraph()
            continue
        if line.startswith("# "):
            flush_paragraph()
            if story:
                story.append(PageBreak())
            story.append(Paragraph(inline_markup(line[2:]), style_map["h1"]))
        elif line.startswith("## "):
            flush_paragraph()
            story.append(Paragraph(inline_markup(line[3:]), style_map["h2"]))
        elif line.startswith("### "):
            flush_paragraph()
            story.append(Paragraph(inline_markup(line[4:]), style_map["h3"]))
        elif line.lstrip().startswith("- "):
            flush_paragraph()
            indent = len(line) - len(line.lstrip())
            item = line.lstrip()[2:]
            marker = "-"
            for candidate in ("[ ]", "[x]", "[~]"):
                if item.startswith(candidate):
                    marker = candidate
                    item = item[3:].strip()
                    break
            bullet_style = ParagraphStyle(
                f"dynamic-{indent}", parent=style_map["bullet"],
                leftIndent=14 + indent * 2,
            )
            story.append(Paragraph(
                f"{escape(marker)} &nbsp; {inline_markup(item)}", bullet_style
            ))
        elif line[0].isdigit() and ". " in line[:4]:
            flush_paragraph()
            number, item = line.split(". ", 1)
            story.append(Paragraph(
                f"{escape(number)}. &nbsp; {inline_markup(item)}",
                style_map["bullet"],
            ))
        else:
            paragraph_lines.append(line)

    flush_paragraph()
    return story


def draw_page(canvas, document) -> None:
    canvas.saveState()
    width, _ = A4
    canvas.setStrokeColor(colors.HexColor("#D7E2E9"))
    canvas.line(20 * mm, 15 * mm, width - 20 * mm, 15 * mm)
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(MUTED)
    canvas.drawString(20 * mm, 9.5 * mm, "TCP Chat Learning Handbook")
    canvas.drawRightString(width - 20 * mm, 9.5 * mm, f"Page {document.page}")
    canvas.restoreState()


def build() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    style_map = make_styles()
    document = SimpleDocTemplate(
        str(OUTPUT), pagesize=A4, rightMargin=20 * mm, leftMargin=20 * mm,
        topMargin=18 * mm, bottomMargin=20 * mm,
        title="TCP Chat Learning Handbook",
        author="TCP Chat Learning Project",
        subject="Python sockets, threading, and progress tracking",
    )

    story = [
        Spacer(1, 42 * mm),
        Paragraph("TCP Chat Learning Handbook", style_map["title"]),
        Paragraph(
            "Python sockets, one-thread-per-client concurrency, and a mastery tree",
            style_map["subtitle"],
        ),
        Spacer(1, 8 * mm),
        Paragraph("How to use this handbook", style_map["h2"]),
        Paragraph(
            "Read a concept, predict the behavior, implement one small step in Vim, "
            "test it, then record evidence in the knowledge tree and learning log. "
            "A checked box means you can explain and demonstrate the skill.",
            style_map["body"],
        ),
        PageBreak(),
    ]

    for source in SOURCES:
        story.extend(markdown_story(source, style_map))

    document.build(story, onFirstPage=draw_page, onLaterPages=draw_page)
    print(OUTPUT)


if __name__ == "__main__":
    build()
