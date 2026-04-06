"""HTML resume preview → PDF using ReportLab (pure Python; no Cairo/wkhtmltopdf)."""
from io import BytesIO
from xml.sax.saxutils import escape

from bs4 import BeautifulSoup
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer


def html_to_pdf_bytes(html: str) -> bytes:
    soup = BeautifulSoup(html or "<html><body></body></html>", "html.parser")
    for tag in soup(["script", "style"]):
        tag.decompose()
    body = soup.find("body") or soup
    text = body.get_text(separator="\n", strip=True)
    if not text.strip():
        text = "Resume preview (no text extracted)."
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]

    buf = BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=letter,
        rightMargin=54,
        leftMargin=54,
        topMargin=54,
        bottomMargin=54,
    )
    styles = getSampleStyleSheet()
    story = []

    if lines:
        story.append(Paragraph(escape(lines[0])[:500], styles["Title"]))
        story.append(Spacer(1, 0.15 * inch))
    for ln in lines[1:]:
        xml = escape(ln)[:3500].replace("\n", "<br/>")
        story.append(Paragraph(xml, styles["Normal"]))
        story.append(Spacer(1, 0.06 * inch))

    doc.build(story)
    data = buf.getvalue()
    if not data:
        raise RuntimeError("Empty PDF output.")
    return data
