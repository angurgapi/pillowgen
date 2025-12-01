from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, StreamingResponse
import io, datetime
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
from imagegen import draw_receipt_png_bytes, draw_receipt_pdf_bytes
from form_template import get_invoice_form_html

app = FastAPI(title="Receipt Generator")

BASE_DIR = Path(__file__).resolve().parent
app = FastAPI(title="Receipt Generator")

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    return FileResponse(BASE_DIR / "static" / "favicon.ico")

@app.get("/", response_class=HTMLResponse)
def form():
    return get_invoice_form_html()

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
