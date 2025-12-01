from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, StreamingResponse
import io, datetime
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
from imagegen import draw_receipt_png_bytes, draw_receipt_pdf_bytes

app = FastAPI(title="Receipt Generator")

BASE_DIR = Path(__file__).resolve().parent
app = FastAPI(title="Receipt Generator")

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    return FileResponse(BASE_DIR / "static" / "favicon.ico")
FORM_HTML = f"""
<!doctype html>
<html>
  <head>
    <meta charset="utf-8"/>
    <title>Receipt Generator</title>
    <link rel="icon" type="image/x-icon" href="/static/favicon.ico">
    <meta name="viewport" content="width=device-width, initial-scale=1"/>
    <style>
      * {{box-sizing: border-box}}
      body{{font-family:ui-sans-serif,-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,Ubuntu,Helvetica,Arial,sans-serif;
           background:#f8fafc;margin:0;padding:24px;}}
      .card{{max-width:900px;margin:0 auto;background:#fff;padding:32px;border-radius:12px;border:1px solid #e5e7eb}}
      h1{{margin:0 0 8px;font-size:24px}}
      h2{{margin:24px 0 12px;font-size:16px;color:#0ea5e9;border-bottom:2px solid #e5e7eb;padding-bottom:8px}}
      .row{{display:grid;grid-template-columns:1fr 1fr;gap:16px}}
      label{{display:block;margin-top:12px;color:#334155;font-size:14px;font-weight:500}}
      input,textarea{{width:100%;padding:10px 12px;margin-top:6px;border:1px solid #cbd5e1;border-radius:8px;font-size:14px;font-family:inherit}}
      textarea{{min-height:80px;resize:vertical}}
      button{{margin-top:24px;padding:12px 24px;border-radius:8px;border:1px solid #0ea5e9;background:#0284c7;color:#fff;font-weight:600;cursor:pointer;font-size:15px}}
      button:hover{{background:#0369a1}}
      small{{color:#64748b}}
      .subtitle{{color:#64748b;font-size:14px;margin-bottom:24px}}
      .header{{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:24px}}
      .paid-checkbox{{display:flex;align-items:center;gap:8px;padding:12px 16px;background:#f0fdf4;border:2px solid #86efac;border-radius:8px;cursor:pointer}}
      .paid-checkbox input{{width:auto;margin:0;cursor:pointer}}
      .paid-checkbox label{{margin:0;cursor:pointer;color:#15803d;font-weight:600}}
    </style>
  </head>
  <body>
    <div class="card">
      <form method="post" action="/generate">
        <div class="header">
          <div>
            <h1>Invoice Generator</h1>
            <p class="subtitle">Create professional invoices in PNG or PDF format</p>
          </div>
          <div class="paid-checkbox">
            <input type="checkbox" id="mark_paid" name="mark_paid" value="yes" />
            <label for="mark_paid">Mark as PAID</label>
          </div>
        </div>
        
        <h2>📄 Invoice Details</h2>
        <div class="row">
          <label>Invoice Number
            <input name="invoice_no" value="2025-55577" required />
          </label>
          <label>Invoice Date
            <input type="date" name="invoice_date" value="{datetime.date.today().strftime("%Y-%m-%d")}" required />
          </label>
        </div>
        <div class="row">
          <label>Due Date
            <input type="date" name="due_date" value="{(datetime.date.today() + datetime.timedelta(days=30)).strftime("%Y-%m-%d")}" required />
          </label>
          <label>Payment Terms
            <input name="payment_terms" value="Net 30" />
          </label>
        </div>
        
        <h2>🏢 Your Company (From)</h2>
        <label>Company Name
          <input name="company_name" value="Your Company Ltd." required />
        </label>
        <div class="row">
          <label>Company Address
            <textarea name="company_address" required>123 Business Street
New York, NY 10001
United States</textarea>
          </label>
          <div>
            <label>Tax/VAT ID
              <input name="company_tax_id" value="US123456789" />
            </label>
            <label>Email
              <input name="company_email" type="email" value="billing@yourcompany.com" />
            </label>
            <label>Phone
              <input name="company_phone" value="+1 (555) 123-4567" />
            </label>
          </div>
        </div>
        
        <h2>👤 Bill To (Client)</h2>
        <label>Client Name/Company
          <input name="client_name" value="Client Company Inc." required />
        </label>
        <div class="row">
          <label>Billing Address
            <textarea name="client_address" required>456 Client Avenue
Los Angeles, CA 90001
United States</textarea>
          </label>
          <div>
            <label>Client Email
              <input name="client_email" type="email" value="contact@client.com" />
            </label>
            <label>Client Phone
              <input name="client_phone" value="+1 (555) 987-6543" />
            </label>
          </div>
        </div>
        
        <h2>💰 Payment Details</h2>
        <div class="row">
          <label>Currency
            <input name="currency" value="USD" required />
          </label>
          <label>Payment Method
            <input name="payment_method" value="Bank Transfer" />
          </label>
        </div>
        
        <h2>📋 Line Items</h2>
        <label>Item Description
          <textarea name="item_description" required>Professional consulting services
Project management and delivery
Technical documentation</textarea>
        </label>
        <div class="row">
          <label>Quantity
            <input name="quantity" type="number" value="1" min="1" required />
          </label>
          <label>Unit Price
            <input name="unit_price" type="number" step="0.01" value="5000.00" required />
          </label>
        </div>
        <div class="row">
          <label>Tax/VAT Rate (%) <small>Leave 0 for no tax</small>
            <input name="tax_rate" type="number" step="0.01" value="0" min="0" />
          </label>
          <label>Discount (%) <small>Leave 0 for no discount</small>
            <input name="discount" type="number" step="0.01" value="0" min="0" />
          </label>
        </div>
        
        <h2>📝 Additional Notes</h2>
        <label>Notes/Terms
          <textarea name="notes">Thank you for your business!
Payment is due within 30 days.
Please include invoice number on payment.</textarea>
        </label>
        
        <label style="margin-top:24px;font-weight:600">Output Format
          <div style="margin-top:8px;display:flex;gap:18px">
            <label style="display:flex;align-items:center;gap:8px;font-weight:normal;cursor:pointer">
              <input type="radio" name="format" value="png" style="margin:0;cursor:pointer" /> PNG
            </label>
            <label style="display:flex;align-items:center;gap:8px;font-weight:normal;cursor:pointer">
              <input type="radio" name="format" value="pdf" checked style="margin:0;cursor:pointer" /> PDF
            </label>
          </div>
        </label>
        <button type="submit">Generate Invoice</button>
      </form>
    </div>
  </body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
def form():
    return FORM_HTML

@app.post("/generate")
def generate(
    # Invoice details
    invoice_no: str = Form(...),
    invoice_date: str = Form(...),
    due_date: str = Form(...),
    payment_terms: str = Form("Net 30"),
    # Company details
    company_name: str = Form(...),
    company_address: str = Form(...),
    company_tax_id: str = Form(""),
    company_email: str = Form(""),
    company_phone: str = Form(""),
    # Client details
    client_name: str = Form(...),
    client_address: str = Form(...),
    client_email: str = Form(""),
    client_phone: str = Form(""),
    # Payment details
    currency: str = Form(...),
    payment_method: str = Form("Bank Transfer"),
    # Line items
    item_description: str = Form(...),
    quantity: str = Form("1"),
    unit_price: str = Form(...),
    tax_rate: str = Form("0"),
    discount: str = Form("0"),
    # Additional
    notes: str = Form(""),
    mark_paid: str = Form(""),
    format: str = Form("pdf"),
):
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    
    # Format dates for display (convert YYYY-MM-DD to readable format)
    def format_date(date_str):
        try:
            date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d")
            return date_obj.strftime("%d %B %Y")
        except:
            return date_str
    
    formatted_invoice_date = format_date(invoice_date)
    formatted_due_date = format_date(due_date)
    
    # Calculate totals
    try:
        qty = float(quantity)
        price = float(unit_price)
        tax = float(tax_rate)
        disc = float(discount)
        
        subtotal = qty * price
        discount_amount = subtotal * (disc / 100)
        subtotal_after_discount = subtotal - discount_amount
        tax_amount = subtotal_after_discount * (tax / 100)
        total = subtotal_after_discount + tax_amount
    except:
        subtotal = 0
        discount_amount = 0
        tax_amount = 0
        total = 0
    
    invoice_data = {
        "invoice_no": invoice_no,
        "invoice_date": formatted_invoice_date,
        "due_date": formatted_due_date,
        "payment_terms": payment_terms,
        "company_name": company_name,
        "company_address": company_address,
        "company_tax_id": company_tax_id,
        "company_email": company_email,
        "company_phone": company_phone,
        "client_name": client_name,
        "client_address": client_address,
        "client_email": client_email,
        "client_phone": client_phone,
        "currency": currency,
        "payment_method": payment_method,
        "item_description": item_description,
        "quantity": qty,
        "unit_price": price,
        "subtotal": subtotal,
        "discount": disc,
        "discount_amount": discount_amount,
        "tax_rate": tax,
        "tax_amount": tax_amount,
        "total": total,
        "notes": notes,
        "is_paid": mark_paid == "yes"
    }
    
    if format == "pdf":
        from imagegen import draw_invoice_pdf_bytes
        pdf = draw_invoice_pdf_bytes(invoice_data)
        filename = f"invoice_{invoice_no}_{timestamp}.pdf"
        headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
        return StreamingResponse(io.BytesIO(pdf), media_type="application/pdf", headers=headers)
    else:
        from imagegen import draw_invoice_png_bytes
        png = draw_invoice_png_bytes(invoice_data)
        filename = f"invoice_{invoice_no}_{timestamp}.png"
        headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
        return StreamingResponse(io.BytesIO(png), media_type="image/png", headers=headers)
