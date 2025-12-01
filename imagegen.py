# imagegen.py
from PIL import Image, ImageDraw, ImageFont
import io
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from receipt_png import draw_receipt_png_bytes
from receipt_pdf import draw_receipt_pdf_bytes

# ---- constants / colors ----
W, H = 1600, 1000
bg = (255, 255, 255)
ink = (17, 24, 39)
muted = (107, 114, 128)
border = (229, 231, 235)
accent = (5, 150, 105)

# ---- font loader: zero-install (try common system fonts, else fallback) ----
COMMON_SANS = [
    "/Library/Fonts/Arial.ttf",                  # macOS
    "/Library/Fonts/Arial Bold.ttf",
    "/System/Library/Fonts/Helvetica.ttc",       # macOS system
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",  # Linux
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "C:/Windows/Fonts/arial.ttf",                # Windows
    "C:/Windows/Fonts/arialbd.ttf",
]

def _load_font(size: int, bold: bool = False):
    candidates = []
    if bold:
        candidates = [p for p in COMMON_SANS if ("Bold" in p or p.lower().endswith("bd.ttf"))]
    else:
        candidates = [p for p in COMMON_SANS if ("Bold" not in p and not p.lower().endswith("bd.ttf"))]
    for p in candidates:
        try:
            return ImageFont.truetype(p, size)
        except Exception:
            pass
    return ImageFont.load_default()

def _font_sm():   return _load_font(30, bold=False)
def _font_body(): return _load_font(36, bold=False)
def _font_h1():   return _load_font(52, bold=True)
def _font_bold(): return _load_font(42, bold=True)


def draw_invoice_pdf_bytes(data: dict) -> bytes:
    """Generate a professional invoice PDF with all details."""
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    width, height = A4
    
    # Colors
    ink = (17/255, 24/255, 39/255)
    muted = (107/255, 114/255, 128/255)
    accent = (5/255, 150/255, 105/255)
    light_bg = (249/255, 250/255, 251/255)
    
    margin = 50
    y = height - 50
    
    # Header - Company Info
    c.setFillColorRGB(*ink)
    c.setFont("Helvetica-Bold", 22)
    c.drawString(margin, y, data["company_name"])
    y -= 20
    
    c.setFont("Helvetica", 9)
    c.setFillColorRGB(*muted)
    for line in data["company_address"].split("\n"):
        c.drawString(margin, y, line.strip())
        y -= 12
    
    if data["company_email"]:
        c.drawString(margin, y, f"Email: {data['company_email']}")
        y -= 12
    if data["company_phone"]:
        c.drawString(margin, y, f"Phone: {data['company_phone']}")
        y -= 12
    if data["company_tax_id"]:
        c.drawString(margin, y, f"Tax ID: {data['company_tax_id']}")
    
    # Invoice Title and Number (right side)
    title_y = height - 50
    c.setFillColorRGB(*accent)
    c.setFont("Helvetica-Bold", 28)
    c.drawRightString(width - margin, title_y, "INVOICE")
    title_y -= 30
    
    c.setFillColorRGB(*ink)
    c.setFont("Helvetica-Bold", 16)
    c.drawRightString(width - margin, title_y, f"# {data['invoice_no']}")
    title_y -= 25
    
    # Invoice dates
    c.setFont("Helvetica", 9)
    c.setFillColorRGB(*muted)
    c.drawRightString(width - margin, title_y, f"Date: {data['invoice_date']}")
    title_y -= 12
    c.drawRightString(width - margin, title_y, f"Due Date: {data['due_date']}")
    
    # PAID stamp if marked as paid
    if data.get("is_paid", False):
        c.saveState()
        c.setFillColorRGB(5/255, 150/255, 105/255)
        c.setStrokeColorRGB(5/255, 150/255, 105/255)
        c.setLineWidth(3)
        c.rotate(15)
        paid_x = width - 150
        paid_y = height - 400
        c.setFont("Helvetica-Bold", 48)
        c.drawString(paid_x, paid_y, "PAID")
        c.rect(paid_x - 10, paid_y - 10, 140, 60, stroke=1, fill=0)
        c.restoreState()
    
    # Bill To section
    y = height - 200
    c.setFillColorRGB(*ink)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(margin, y, "BILL TO:")
    y -= 18
    
    c.setFont("Helvetica-Bold", 10)
    c.drawString(margin, y, data["client_name"])
    y -= 14
    
    c.setFont("Helvetica", 9)
    c.setFillColorRGB(*muted)
    for line in data["client_address"].split("\n"):
        c.drawString(margin, y, line.strip())
        y -= 12
    
    if data["client_email"]:
        c.drawString(margin, y, data["client_email"])
        y -= 12
    if data["client_phone"]:
        c.drawString(margin, y, data["client_phone"])
    
    # Payment info box (right side)
    info_y = height - 200
    info_x = width - 250
    c.setFillColorRGB(*muted)
    c.setFont("Helvetica", 9)
    c.drawString(info_x, info_y, "Payment Terms:")
    c.setFillColorRGB(*ink)
    c.drawString(info_x + 90, info_y, data["payment_terms"])
    info_y -= 14
    
    c.setFillColorRGB(*muted)
    c.drawString(info_x, info_y, "Payment Method:")
    c.setFillColorRGB(*ink)
    c.drawString(info_x + 90, info_y, data["payment_method"])
    info_y -= 14
    
    c.setFillColorRGB(*muted)
    c.drawString(info_x, info_y, "Currency:")
    c.setFillColorRGB(*ink)
    c.drawString(info_x + 90, info_y, data["currency"])
    
    # Items table
    y = height - 340
    table_top = y
    
    # Table header
    c.setFillColorRGB(0.95, 0.96, 0.97)
    c.rect(margin, y - 20, width - 2*margin, 25, fill=1, stroke=0)
    
    c.setFillColorRGB(*ink)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(margin + 10, y - 5, "DESCRIPTION")
    c.drawRightString(width - margin - 230, y - 5, "QTY")
    c.drawRightString(width - margin - 130, y - 5, "UNIT PRICE")
    c.drawRightString(width - margin - 10, y - 5, "AMOUNT")
    
    y -= 35
    
    # Item row
    c.setFont("Helvetica", 9)
    c.setFillColorRGB(*ink)
    
    # Word wrap description
    desc_lines = data["item_description"].split("\n")
    for line in desc_lines[:5]:  # Max 5 lines
        c.drawString(margin + 10, y, line.strip()[:80])
        y -= 12
    
    item_y = table_top - 30
    c.drawRightString(width - margin - 230, item_y, str(int(data["quantity"])))
    c.drawRightString(width - margin - 130, item_y, f"{data['unit_price']:.2f}")
    c.drawRightString(width - margin - 10, item_y, f"{data['subtotal']:.2f}")
    
    # Totals section
    y = height - 520
    totals_x = width - margin - 200
    
    c.setStrokeColorRGB(0.9, 0.9, 0.9)
    c.line(totals_x - 10, y + 10, width - margin, y + 10)
    
    c.setFont("Helvetica", 9)
    c.setFillColorRGB(*muted)
    
    # Subtotal
    c.drawString(totals_x, y, "Subtotal:")
    c.setFillColorRGB(*ink)
    c.drawRightString(width - margin - 10, y, f"{data['currency']} {data['subtotal']:.2f}")
    y -= 18
    
    # Discount
    if data["discount"] > 0:
        c.setFillColorRGB(*muted)
        c.drawString(totals_x, y, f"Discount ({data['discount']:.1f}%):")
        c.setFillColorRGB(*ink)
        c.drawRightString(width - margin - 10, y, f"-{data['currency']} {data['discount_amount']:.2f}")
        y -= 18
    
    # Tax
    if data["tax_rate"] > 0:
        c.setFillColorRGB(*muted)
        c.drawString(totals_x, y, f"Tax ({data['tax_rate']:.1f}%):")
        c.setFillColorRGB(*ink)
        c.drawRightString(width - margin - 10, y, f"{data['currency']} {data['tax_amount']:.2f}")
        y -= 18
    
    # Total
    c.setStrokeColorRGB(0.9, 0.9, 0.9)
    c.line(totals_x - 10, y + 5, width - margin, y + 5)
    y -= 15
    
    c.setFont("Helvetica-Bold", 12)
    c.setFillColorRGB(*ink)
    c.drawString(totals_x, y, "Total:")
    c.drawRightString(width - margin - 10, y, f"{data['currency']} {data['total']:.2f}")
    
    # Notes section
    if data["notes"]:
        y = 150
        c.setFont("Helvetica-Bold", 9)
        c.setFillColorRGB(*ink)
        c.drawString(margin, y, "NOTES:")
        y -= 15
        
        c.setFont("Helvetica", 8)
        c.setFillColorRGB(*muted)
        for line in data["notes"].split("\n")[:5]:
            c.drawString(margin, y, line.strip())
            y -= 12
    
    # Footer
    c.setFont("Helvetica", 8)
    c.setFillColorRGB(*muted)
    c.drawCentredString(width/2, 40, f"Invoice {data['invoice_no']} - Page 1")
    
    c.showPage()
    c.save()
    
    buf.seek(0)
    return buf.getvalue()


def draw_invoice_png_bytes(data: dict) -> bytes:
    """Generate a professional invoice PNG with all details."""
    im = Image.new("RGB", (W, H), bg)
    d = ImageDraw.Draw(im)
    
    f_sm = _font_sm()
    f_body = _font_body()
    f_h1 = _font_h1()
    f_bold = _font_bold()
    
    margin = 60
    content_width = W - 2 * margin
    left_col_width = int(content_width * 0.40)
    gap = 40
    right_col_x = margin + left_col_width + gap
    
    x = margin
    y = margin
    
    # Company header (left side - 40%)
    d.text((x, y), data["company_name"], font=f_bold, fill=ink)
    y += 50
    
    # Company address lines
    addr_lines = data["company_address"].split("\n")[:3]
    for line in addr_lines:
        d.text((x, y), line.strip()[:40], font=f_sm, fill=muted)
        y += 28
    
    if data["company_email"]:
        d.text((x, y), data["company_email"][:40], font=f_sm, fill=muted)
        y += 28
    if data["company_phone"]:
        d.text((x, y), data["company_phone"][:40], font=f_sm, fill=muted)
    
    # Invoice title (right side - 60%)
    title_x = right_col_x
    title_y = margin
    d.text((title_x, title_y), "INVOICE", font=f_h1, fill=accent)
    title_y += 65
    d.text((title_x, title_y), f"# {data['invoice_no']}", font=f_bold, fill=ink)
    title_y += 45
    d.text((title_x, title_y), f"Date: {data['invoice_date']}", font=f_sm, fill=muted)
    title_y += 30
    d.text((title_x, title_y), f"Due: {data['due_date']}", font=f_sm, fill=muted)
    
    # PAID stamp if marked as paid
    if data.get("is_paid", False):
        from PIL import ImageFont
        paid_font = _load_font(80, bold=True)
        paid_text = "PAID"
        # Position for rotated text (center area)
        paid_x = W - 400
        paid_y = 400
        # Create a temporary image for rotation
        temp_im = Image.new("RGBA", (300, 150), (255, 255, 255, 0))
        temp_d = ImageDraw.Draw(temp_im)
        temp_d.text((20, 30), paid_text, font=paid_font, fill=accent)
        temp_d.rectangle((15, 25, 220, 120), outline=accent, width=8)
        # Rotate and paste
        rotated = temp_im.rotate(15, expand=True)
        im.paste(rotated, (paid_x, paid_y), rotated)
    
    # Bill To section (left column - 40%)
    y = 280
    d.text((x, y), "BILL TO:", font=f_bold, fill=ink)
    y += 38
    d.text((x, y), data["client_name"][:35], font=f_body, fill=ink)
    y += 38
    
    # Client address
    client_addr_lines = data["client_address"].split("\n")[:3]
    for line in client_addr_lines:
        d.text((x, y), line.strip()[:40], font=f_sm, fill=muted)
        y += 28
    
    # Payment info (right column - 60%)
    info_x = right_col_x
    info_y = 280
    d.text((info_x, info_y), "Payment Terms:", font=f_sm, fill=muted)
    info_y += 28
    d.text((info_x, info_y), data["payment_terms"][:30], font=f_sm, fill=ink)
    info_y += 35
    d.text((info_x, info_y), "Payment Method:", font=f_sm, fill=muted)
    info_y += 28
    d.text((info_x, info_y), data["payment_method"][:30], font=f_sm, fill=ink)
    
    # Table header
    y = 480
    table_y = y
    d.rectangle((margin, y, W - margin, y + 45), fill=(240, 240, 240))
    
    # Column positions
    desc_col = margin + 20
    qty_col = margin + left_col_width - 100
    price_col = right_col_x + 100
    amount_col = W - margin - 20
    
    d.text((desc_col, y + 12), "Description", font=f_body, fill=ink)
    d.text((qty_col, y + 12), "Qty", font=f_body, fill=ink)
    d.text((price_col, y + 12), "Unit Price", font=f_body, fill=ink)
    d.text((amount_col, y + 12), "Amount", font=f_body, fill=ink, anchor="ra")
    
    # Item row
    y += 65
    item_y = y
    desc_lines = data["item_description"].split("\n")
    for i, line in enumerate(desc_lines[:3]):
        d.text((desc_col, y), line.strip()[:45], font=f_sm, fill=ink)
        y += 30
    
    # Item values aligned to first description line
    d.text((qty_col, item_y), str(int(data["quantity"])), font=f_body, fill=ink)
    d.text((price_col, item_y), f"{data['unit_price']:.2f}", font=f_body, fill=ink)
    d.text((amount_col, item_y), f"{data['subtotal']:.2f}", font=f_body, fill=ink, anchor="ra")
    
    # Totals section (aligned to right column)
    y = max(y + 40, 720)
    d.line((margin, y, W - margin, y), fill=border, width=2)
    y += 30
    
    totals_label_x = right_col_x
    totals_value_x = W - margin - 20
    
    d.text((totals_label_x, y), "Subtotal:", font=f_body, fill=muted)
    d.text((totals_value_x, y), f"{data['currency']} {data['subtotal']:.2f}", font=f_body, fill=ink, anchor="ra")
    y += 40
    
    if data["discount"] > 0:
        d.text((totals_label_x, y), f"Discount ({data['discount']:.1f}%):", font=f_body, fill=muted)
        d.text((totals_value_x, y), f"-{data['currency']} {data['discount_amount']:.2f}", font=f_body, fill=ink, anchor="ra")
        y += 40
    
    if data["tax_rate"] > 0:
        d.text((totals_label_x, y), f"Tax ({data['tax_rate']:.1f}%):", font=f_body, fill=muted)
        d.text((totals_value_x, y), f"{data['currency']} {data['tax_amount']:.2f}", font=f_body, fill=ink, anchor="ra")
        y += 40
    
    d.line((totals_label_x - 20, y, W - margin, y), fill=border, width=3)
    y += 20
    d.text((totals_label_x, y), "Total:", font=f_bold, fill=ink)
    d.text((totals_value_x, y), f"{data['currency']} {data['total']:.2f}", font=f_bold, fill=ink, anchor="ra")
    
    # Notes section at bottom
    if data["notes"]:
        y = H - 160
        d.text((margin, y), "NOTES:", font=f_bold, fill=ink)
        y += 38
        note_lines = data["notes"].split("\n")[:3]
        for line in note_lines:
            d.text((margin, y), line.strip()[:90], font=f_sm, fill=muted)
            y += 28
    
    buf = io.BytesIO()
    im.save(buf, format="PNG")
    buf.seek(0)
    return buf.getvalue()
