from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer,
    HRFlowable, Table, TableStyle,
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import io
import re
from datetime import datetime

# ── Palette ───────────────────────────────────────────────────────────────────
NIKE_BLACK  = colors.HexColor("#111111")
NIKE_ORANGE = colors.HexColor("#FF6600")   # Nike brand orange
ACCENT_GRAY = colors.HexColor("#F5F5F5")
MID_GRAY    = colors.HexColor("#888888")
TEXT_DARK   = colors.HexColor("#1A1A1A")
WHITE       = colors.white
RULE_COLOR  = colors.HexColor("#E0E0E0")


def _styles() -> dict:
    return {
        "report_title": ParagraphStyle(
            "report_title",
            fontName="Helvetica-Bold",
            fontSize=20,
            textColor=WHITE,
            leading=24,
            spaceAfter=3,
        ),
        "report_sub": ParagraphStyle(
            "report_sub",
            fontName="Helvetica",
            fontSize=9,
            textColor=colors.HexColor("#CCCCCC"),
            leading=14,
            spaceAfter=2,
        ),
        "section_header": ParagraphStyle(
            "section_header",
            fontName="Helvetica-Bold",
            fontSize=11,
            textColor=NIKE_ORANGE,
            spaceBefore=12,
            spaceAfter=5,
            leading=15,
        ),
        "body": ParagraphStyle(
            "body",
            fontName="Helvetica",
            fontSize=9,
            textColor=TEXT_DARK,
            leading=14,
            spaceAfter=4,
        ),
        "bullet": ParagraphStyle(
            "bullet",
            fontName="Helvetica",
            fontSize=9,
            textColor=TEXT_DARK,
            leading=14,
            leftIndent=14,
            spaceAfter=3,
        ),
        "footer": ParagraphStyle(
            "footer",
            fontName="Helvetica",
            fontSize=7,
            textColor=MID_GRAY,
            alignment=TA_CENTER,
        ),
        "meta_label": ParagraphStyle(
            "meta_label",
            fontName="Helvetica-Bold",
            fontSize=7.5,
            textColor=colors.HexColor("#AAAAAA"),
            leading=11,
        ),
        "meta_value": ParagraphStyle(
            "meta_value",
            fontName="Helvetica",
            fontSize=8.5,
            textColor=WHITE,
            leading=12,
        ),
    }


def _inline(text: str) -> str:
    """Convert **bold** / *italic* markdown to ReportLab tags."""
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"\*(.+?)\*",     r"<i>\1</i>", text)
    return text


def _md_to_flowables(markdown: str, styles: dict) -> list:
    flowables = []
    for line in markdown.split("\n"):
        line = line.strip()
        if not line:
            flowables.append(Spacer(1, 4))
            continue

        if line.startswith("## "):
            flowables.append(HRFlowable(
                width="100%", thickness=0.4, color=RULE_COLOR, spaceAfter=3
            ))
            flowables.append(Paragraph(line[3:].strip(), styles["section_header"]))

        elif line.startswith("- "):
            flowables.append(
                Paragraph(f"• {_inline(line[2:].strip())}", styles["bullet"])
            )

        elif re.match(r"^\d+\.\s", line):
            content = re.sub(r"^\d+\.\s", "", line).strip()
            flowables.append(
                Paragraph(f"• {_inline(content)}", styles["bullet"])
            )

        elif line.startswith("---"):
            flowables.append(Spacer(1, 3))
            flowables.append(HRFlowable(
                width="100%", thickness=0.8, color=RULE_COLOR, spaceAfter=3
            ))

        else:
            flowables.append(Paragraph(_inline(line), styles["body"]))

    return flowables


def generate_pdf(
    report_markdown: str,
    product_name: str,
    company_url: str,
    target_customer: str,
) -> bytes:
    """Render the sales intelligence report as a PDF and return bytes."""

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=0.65 * inch,
        rightMargin=0.65 * inch,
        topMargin=0.45 * inch,
        bottomMargin=0.55 * inch,
    )

    s = _styles()
    story = []

    # ── Header banner ──────────────────────────────────────────────────────────
    left_cell = [
        Paragraph("SALES INTELLIGENCE BRIEF", s["report_sub"]),
        Paragraph("Nike, Inc.", s["report_title"]),
        Paragraph(
            f"Prepared for: <b>{target_customer}</b>  ·  "
            f"Date: {datetime.today().strftime('%B %d, %Y')}",
            s["report_sub"],
        ),
    ]

    right_cell = [
        Paragraph("PRODUCT", s["meta_label"]),
        Paragraph(product_name, s["meta_value"]),
        Spacer(1, 6),
        Paragraph("PROSPECT URL", s["meta_label"]),
        Paragraph(company_url, s["meta_value"]),
    ]

    header_tbl = Table(
        [[left_cell, right_cell]],
        colWidths=[4.3 * inch, 2.8 * inch],
    )
    header_tbl.setStyle(TableStyle([
        ("BACKGROUND",   (0, 0), (-1, -1), NIKE_BLACK),
        ("VALIGN",       (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING",  (0, 0), (-1, -1), 18),
        ("RIGHTPADDING", (0, 0), (-1, -1), 18),
        ("TOPPADDING",   (0, 0), (-1, -1), 18),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 18),
        # Orange left accent bar
        ("LINEBEFORE",   (0, 0), (0, 0), 5, NIKE_ORANGE),
    ]))
    story.append(header_tbl)
    story.append(Spacer(1, 14))

    # ── Report body ────────────────────────────────────────────────────────────
    story.extend(_md_to_flowables(report_markdown, s))
    story.append(Spacer(1, 18))

    # ── Footer ─────────────────────────────────────────────────────────────────
    story.append(HRFlowable(width="100%", thickness=0.5, color=MID_GRAY))
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        "CONFIDENTIAL  ·  Generated by Sales Intelligence Agent  ·  For internal use only  ·  nike.com",
        s["footer"],
    ))

    doc.build(story)
    return buffer.getvalue()
