# receipt_pdf.py
import io
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


def draw_receipt_pdf_bytes(
    company_name: str,
    receipt_no: str,
    received_from: str,
    receipt_date: str,
    currency: str,
    totalsum: str,
    description: str,
) -> bytes:
    """Return a PDF document (as bytes) of a single-line, PAID receipt."""
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    width, height = A4
    
    try:
        amount = float(totalsum)
    except Exception:
        amount = 0.0
    
    # Colors (RGB 0-1 scale)
    ink_color = (17/255, 24/255, 39/255)
    muted_color = (107/255, 114/255, 128/255)
    accent_color = (5/255, 150/255, 105/255)
    
    y = height - 60
    margin = 50
    
    # Header - Company Name
    c.setFillColorRGB(*ink_color)
    c.setFont("Helvetica-Bold", 20)
    c.drawString(margin, y, company_name)
    y -= 25
    
    c.setFillColorRGB(*muted_color)
    c.setFont("Helvetica", 10)
    c.drawString(margin, y, "Street, City, Country · VAT/Tax ID: —")
    y -= 40
    
    # PAID status
    c.setFillColorRGB(*accent_color)
    c.setFont("Helvetica-Bold", 14)
    c.drawRightString(width - margin, height - 60, "PAID")
    
    # Receipt Number
    c.setFillColorRGB(*muted_color)
    c.setFont("Helvetica", 10)
    c.drawRightString(width - margin, height - 90, "Receipt No.")
    c.setFillColorRGB(*ink_color)
    c.setFont("Helvetica-Bold", 14)
    c.drawRightString(width - margin, height - 108, receipt_no)
    
    # Title
    c.setFillColorRGB(*ink_color)
    c.setFont("Helvetica-Bold", 24)
    c.drawString(margin, y, "Payment Receipt")
    y -= 25
    
    c.setFillColorRGB(*muted_color)
    c.setFont("Helvetica", 11)
    c.drawString(margin, y, "Acknowledgement of funds received for the service below.")
    y -= 50
    
    # Receipt Details (right side)
    detail_x = width - 270
    detail_y = height - 180
    c.setFillColorRGB(*muted_color)
    c.setFont("Helvetica", 10)
    line_height = 20
    
    details = [
        ("Receipt Date", receipt_date),
        ("Payment Method", "Bank transfer"),
        ("Payment Account", "Main account"),
        ("Currency", currency)
    ]
    
    for i, (label, value) in enumerate(details):
        c.drawString(detail_x, detail_y - i * line_height, label)
        c.setFillColorRGB(*ink_color)
        c.setFont("Helvetica", 11)
        c.drawString(detail_x + 120, detail_y - i * line_height, value)
        c.setFillColorRGB(*muted_color)
        c.setFont("Helvetica", 10)
    
    # Parties section
    y -= 30
    c.setStrokeColorRGB(229/255, 231/255, 235/255)
    c.line(margin, y, width - margin, y)
    y -= 20
    
    c.setFillColorRGB(*muted_color)
    c.setFont("Helvetica", 10)
    c.drawString(margin, y, "Received From")
    c.drawString(width - 320, y, "Received By")
    y -= 18
    
    c.setFillColorRGB(*ink_color)
    c.setFont("Helvetica", 12)
    c.drawString(margin, y, received_from)
    c.drawString(width - 320, y, company_name)
    y -= 50
    
    # Items table
    c.setStrokeColorRGB(229/255, 231/255, 235/255)
    c.line(margin, y, width - margin, y)
    y -= 15
    
    c.setFillColorRGB(*muted_color)
    c.setFont("Helvetica", 10)
    c.drawString(margin, y, "Description")
    c.drawRightString(width - 280, y, "Quantity")
    c.drawRightString(width - 160, y, "Price")
    c.drawRightString(width - margin, y, "Total")
    y -= 15
    
    c.line(margin, y, width - margin, y)
    y -= 20
    
    # Item row
    c.setFillColorRGB(*ink_color)
    c.setFont("Helvetica", 11)
    c.drawString(margin, y, description[:50])  # Truncate if too long
    c.drawRightString(width - 280, y, "1")
    c.drawRightString(width - 160, y, f"{amount:.2f} {currency}")
    c.drawRightString(width - margin, y, f"{amount:.2f} {currency}")
    y -= 30
    
    # Total line
    c.line(margin, y, width - margin, y)
    y -= 20
    
    c.setFont("Helvetica-Bold", 14)
    c.drawRightString(width - margin, y, f"Total Received {amount:.2f} {currency}")
    
    c.showPage()
    c.save()
    
    buf.seek(0)
    return buf.getvalue()
