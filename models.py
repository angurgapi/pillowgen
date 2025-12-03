# models.py
from pydantic import BaseModel, ConfigDict, Field
from typing import Union


class InvoiceRequest(BaseModel):
    """Pydantic model for API invoice requests with camelCase support"""
    model_config = ConfigDict(populate_by_name=True)
    
    invoice_no: str = Field(..., alias="invoiceNo")
    invoice_date: str = Field(..., alias="invoiceDate")
    due_date: str = Field(..., alias="dueDate")
    payment_terms: str = Field(default="Net 30", alias="paymentTerms")
    company_name: str = Field(..., alias="companyName")
    company_address: str = Field(..., alias="companyAddress")
    company_tax_id: str = Field(default="", alias="companyTaxId")
    company_email: str = Field(default="", alias="companyEmail")
    company_phone: str = Field(default="", alias="companyPhone")
    client_name: str = Field(..., alias="clientName")
    client_address: str = Field(..., alias="clientAddress")
    client_email: str = Field(default="", alias="clientEmail")
    client_phone: str = Field(default="", alias="clientPhone")
    currency: str
    payment_method: str = Field(default="Bank Transfer", alias="paymentMethod")
    item_description: str = Field(..., alias="itemDescription")
    quantity: Union[str, int, float] = "1"
    unit_price: Union[str, int, float] = Field(..., alias="unitPrice")
    tax_rate: Union[str, int, float] = Field(default="0", alias="taxRate")
    discount: Union[str, int, float] = "0"
    notes: str = ""
    mark_paid: bool = Field(default=False, alias="markPaid")
    format: str = "pdf"
