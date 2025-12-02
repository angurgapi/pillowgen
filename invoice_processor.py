# invoice_processor.py
import datetime
import io
from typing import Dict, Any, Union
from models import InvoiceRequest


def format_date(date_str: str) -> str:
    """Format date from YYYY-MM-DD to DD Month YYYY"""
    try:
        date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d")
        return date_obj.strftime("%d %B %Y")
    except:
        return date_str


def calculate_totals(quantity: Union[str, int, float], 
                     unit_price: Union[str, int, float],
                     tax_rate: Union[str, int, float],
                     discount: Union[str, int, float]) -> Dict[str, float]:
    """Calculate invoice financial totals"""
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
        
        return {
            "quantity": qty,
            "unit_price": price,
            "subtotal": subtotal,
            "discount": disc,
            "discount_amount": discount_amount,
            "tax_rate": tax,
            "tax_amount": tax_amount,
            "total": total
        }
    except:
        return {
            "quantity": 0,
            "unit_price": 0,
            "subtotal": 0,
            "discount": 0,
            "discount_amount": 0,
            "tax_rate": 0,
            "tax_amount": 0,
            "total": 0
        }


def process_invoice_data(invoice_data: Union[InvoiceRequest, Dict[str, Any]], 
                         is_form_data: bool = False) -> Dict[str, Any]:
    """Process and format invoice data for generation"""
    if isinstance(invoice_data, InvoiceRequest):
        # API request
        invoice_date = invoice_data.invoice_date
        due_date = invoice_data.due_date
        is_paid = invoice_data.mark_paid
        quantity = invoice_data.quantity
        unit_price = invoice_data.unit_price
        tax_rate = invoice_data.tax_rate
        discount = invoice_data.discount
    else:
        # Form data
        invoice_date = invoice_data.get("invoice_date")
        due_date = invoice_data.get("due_date")
        is_paid = invoice_data.get("mark_paid") == "yes"
        quantity = invoice_data.get("quantity", "1")
        unit_price = invoice_data.get("unit_price")
        tax_rate = invoice_data.get("tax_rate", "0")
        discount = invoice_data.get("discount", "0")
    
    formatted_invoice_date = format_date(invoice_date)
    formatted_due_date = format_date(due_date)
    
    totals = calculate_totals(quantity, unit_price, tax_rate, discount)
    
    if isinstance(invoice_data, InvoiceRequest):
        processed = {
            "invoice_no": invoice_data.invoice_no,
            "invoice_date": formatted_invoice_date,
            "due_date": formatted_due_date,
            "payment_terms": invoice_data.payment_terms,
            "company_name": invoice_data.company_name,
            "company_address": invoice_data.company_address,
            "company_tax_id": invoice_data.company_tax_id,
            "company_email": invoice_data.company_email,
            "company_phone": invoice_data.company_phone,
            "client_name": invoice_data.client_name,
            "client_address": invoice_data.client_address,
            "client_email": invoice_data.client_email,
            "client_phone": invoice_data.client_phone,
            "currency": invoice_data.currency,
            "payment_method": invoice_data.payment_method,
            "item_description": invoice_data.item_description,
            "notes": invoice_data.notes,
            "is_paid": is_paid
        }
    else:
        processed = {
            "invoice_no": invoice_data.get("invoice_no"),
            "invoice_date": formatted_invoice_date,
            "due_date": formatted_due_date,
            "payment_terms": invoice_data.get("payment_terms", "Net 30"),
            "company_name": invoice_data.get("company_name"),
            "company_address": invoice_data.get("company_address"),
            "company_tax_id": invoice_data.get("company_tax_id", ""),
            "company_email": invoice_data.get("company_email", ""),
            "company_phone": invoice_data.get("company_phone", ""),
            "client_name": invoice_data.get("client_name"),
            "client_address": invoice_data.get("client_address"),
            "client_email": invoice_data.get("client_email", ""),
            "client_phone": invoice_data.get("client_phone", ""),
            "currency": invoice_data.get("currency"),
            "payment_method": invoice_data.get("payment_method", "Bank Transfer"),
            "item_description": invoice_data.get("item_description"),
            "notes": invoice_data.get("notes", ""),
            "is_paid": is_paid
        }
    
    processed.update(totals)
    return processed


def generate_invoice_bytes(processed_data: Dict[str, Any], format: str) -> bytes:
    """Generate invoice as PDF or PNG bytes"""
    if format == "pdf":
        from imagegen import draw_invoice_pdf_bytes
        return draw_invoice_pdf_bytes(processed_data)
    else:
        from imagegen import draw_invoice_png_bytes
        return draw_invoice_png_bytes(processed_data)
