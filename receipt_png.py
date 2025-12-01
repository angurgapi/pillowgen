# receipt_png.py
from PIL import Image, ImageDraw, ImageFont
import io

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


def draw_receipt_png_bytes(
    company_name: str,
    receipt_no: str,
    received_from: str,
    receipt_date: str,
    currency: str,
    totalsum: str,
    description: str,
) -> bytes:
    """Return a PNG image (as bytes) of a single-line, PAID receipt."""
    im = Image.new("RGB", (W, H), bg)
    d = ImageDraw.Draw(im)

    def ts(txt, font):
        x0, y0, x1, y1 = d.textbbox((0, 0), txt, font=font)
        return x1 - x0, y1 - y0

    # Fixed text (always PAID, qty = 1)
    TITLE = "Payment Receipt"
    SUB   = "Acknowledgement of funds received for the service below."
    COMPANY_ADDR = "Street, City, Country · VAT/Tax ID: —"
    PMETHOD = "Bank transfer"
    PACCOUNT = "Main account"

    try:
        amount = float(totalsum)
    except Exception:
        amount = 0.0
    unit_text = f"{amount:.2f} {currency}"
    tot_text  = f"{amount:.2f} {currency}"

    f_sm   = _font_sm()
    f_body = _font_body()
    f_h1   = _font_h1()
    f_bold = _font_bold()

    # Card
    card_m, pad = 60, 56
    x0, y0 = card_m + pad, card_m + pad
    x1, y1 = W - card_m - pad, H - card_m - pad
    d.rounded_rectangle((card_m, card_m, W - card_m, H - card_m), radius=28,
                        outline=border, width=2, fill=bg)

    # Header
    d.text((x0, y0), company_name, font=f_bold, fill=ink)
    d.text((x0, y0 + 44), COMPANY_ADDR, font=f_sm, fill=muted)

    # PAID + receipt no
    tw, th = ts("PAID", f_sm)
    d.text((x1 - (tw + 28) + 14, y0 + 5), "PAID", font=f_sm, fill=accent)
    cap = "Receipt No."
    cap_w, cap_h = ts(cap, f_sm)
    inv_w, inv_h = ts(receipt_no, f_bold)
    cap_x = x1 - cap_w
    cap_y = y0 + (th + 10) + 14
    d.text((cap_x, cap_y), cap, font=f_sm, fill=muted)
    d.text((x1 - inv_w, cap_y + cap_h + 6), receipt_no, font=f_bold, fill=ink)

    # Title
    title_y = y0 + 120
    d.text((x0, title_y), TITLE, font=f_h1, fill=ink)
    d.text((x0, title_y + 58), SUB, font=f_sm, fill=muted)
    left_bottom = title_y + 58 + ts(SUB, f_sm)[1]

    # Right KV
    kv_start = title_y; kv_lbl = x1 - 470; kv_val = x1 - 210; lh = 46
    def kv(y, k, v):
        d.text((kv_lbl, y), k, font=f_sm, fill=muted)
        d.text((kv_val, y), v, font=f_body, fill=ink)
    kv(kv_start + 0 * lh, "Receipt Date", receipt_date)
    kv(kv_start + 1 * lh, "Payment Method", PMETHOD)
    kv(kv_start + 2 * lh, "Payment Account", PACCOUNT)
    kv(kv_start + 3 * lh, "Currency", currency)
    kv_bottom = kv_start + 4 * lh

    # Parties
    parties_top = max(left_bottom, kv_bottom) + 36
    d.line((x0, parties_top, x1, parties_top), fill=border, width=2)
    py = parties_top + 20
    d.text((x0, py), "Received From", font=f_sm, fill=muted)
    d.text((x0, py + 32), received_from, font=f_body, fill=ink)
    rx = x1 - 520
    d.text((rx, py), "Received By", font=f_sm, fill=muted)
    d.text((rx, py + 32), company_name, font=f_body, fill=ink)

    # Items
    items_top = py + 110 + 40
    d.line((x0, items_top, x1, items_top), fill=border, width=2)
    col_qty, col_unit, col_tot = x1 - 540, x1 - 300, x1 - 40
    hdr_y = items_top + 18
    d.text((x0, hdr_y), "Description", font=f_sm, fill=muted)
    d.text((col_qty, hdr_y), "Quantity", font=f_sm, fill=muted, anchor="ra")
    d.text((col_unit, hdr_y), "Price", font=f_sm, fill=muted, anchor="ra")
    d.text((col_tot, hdr_y), "Total", font=f_sm, fill=muted, anchor="ra")
    d.line((x0, hdr_y + 36, x1, hdr_y + 36), fill=border, width=2)

    row_y = hdr_y + 60
    d.text((x0, row_y), description, font=f_body, fill=ink)
    d.text((col_qty, row_y), "1", font=f_body, fill=ink, anchor="ra")
    d.text((col_unit, row_y), unit_text, font=f_body, fill=ink, anchor="ra")
    d.text((col_tot, row_y), tot_text, font=f_body, fill=ink, anchor="ra")

    # Total
    tot_line_y = row_y + 70
    d.line((x0, tot_line_y, x1, tot_line_y), fill=border, width=2)
    tot_y = tot_line_y + 20
    d.text((col_unit, tot_y), "Total Received " + tot_text, font=f_bold, fill=ink, anchor="ra")

    # PNG bytes
    buf = io.BytesIO()
    im.save(buf, format="PNG")
    buf.seek(0)
    return buf.getvalue()
