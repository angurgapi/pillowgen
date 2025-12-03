# api/routes.py
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
import io
import datetime

from models import InvoiceRequest
from services.invoice_service import process_invoice_data, generate_invoice_bytes

router = APIRouter(prefix="/api", tags=["api"])


@router.get("/health")
def health_check():
    """Public health check endpoint"""
    return {"status": "ok", "service": "invoice-generator"}


@router.post("/generate")
def generate_invoice_api(invoice_data: InvoiceRequest):
    """
    API endpoint to generate invoices from external clients.
    Open to all clients without authentication.
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
