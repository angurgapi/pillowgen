from fastapi import FastAPI, Form, HTTPException, Depends
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
import io, datetime

from models import InvoiceRequest
from auth import verify_api_key
from form_template import get_invoice_form_html
from invoice_processor import process_invoice_data, generate_invoice_bytes

BASE_DIR = Path(__file__).resolve().parent
app = FastAPI(title="Invoice Generator API")

# Enable CORS for external clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    return FileResponse(BASE_DIR / "static" / "favicon.ico")


@app.get("/", response_class=HTMLResponse)
def form():
    return get_invoice_form_html()


@app.get("/api/health")
def health_check():
    """Public health check endpoint"""
    return {"status": "ok", "service": "invoice-generator"}


@app.post("/api/generate")
def generate_invoice_api(
    invoice_data: InvoiceRequest,
    api_key: str = Depends(verify_api_key)
):
    """
    API endpoint to generate invoices from external clients.
    Requires X-API-Key header with valid secret.
    """
    try:
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        processed_data = process_invoice_data(invoice_data)
        invoice_bytes = generate_invoice_bytes(processed_data, invoice_data.format)
        
        ext = "pdf" if invoice_data.format == "pdf" else "png"
        media_type = "application/pdf" if invoice_data.format == "pdf" else "image/png"
        filename = f"invoice_{invoice_data.invoice_no}_{timestamp}.{ext}"
        headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
        
        return StreamingResponse(io.BytesIO(invoice_bytes), media_type=media_type, headers=headers)
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating invoice: {str(e)}")

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
    
    form_data = {
        "invoice_no": invoice_no,
        "invoice_date": invoice_date,
        "due_date": due_date,
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
        "quantity": quantity,
        "unit_price": unit_price,
        "tax_rate": tax_rate,
        "discount": discount,
        "notes": notes,
        "mark_paid": mark_paid
    }
    
    processed_data = process_invoice_data(form_data, is_form_data=True)
    invoice_bytes = generate_invoice_bytes(processed_data, format)
    
    ext = "pdf" if format == "pdf" else "png"
    media_type = "application/pdf" if format == "pdf" else "image/png"
    filename = f"invoice_{invoice_no}_{timestamp}.{ext}"
    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
    
    return StreamingResponse(io.BytesIO(invoice_bytes), media_type=media_type, headers=headers)
