# API Documentation

## Invoice Generator API

This API allows external client applications to generate invoices programmatically.

### Authentication

All API endpoints (except health check) require authentication using an API key.

**Header Required:**

```
X-API-Key: your-secret-api-key
```

The API key is automatically generated on server startup and printed to the console. You can also set it as an environment variable:

```bash
export API_SECRET_KEY='your-secret-key-here'
```

---

## Endpoints

### 1. Health Check (Public)

**GET** `/api/health`

Check if the API is running.

**Response:**

```json
{
  "status": "ok",
  "service": "invoice-generator"
}
```

---

### 2. Generate Invoice (Protected)

**POST** `/api/generate`

Generate an invoice in PDF or PNG format.

**Headers:**

```
Content-Type: application/json
X-API-Key: your-secret-api-key
```

**Request Body:**

```json
{
  "invoice_no": "2025-55577",
  "invoice_date": "2025-12-02",
  "due_date": "2026-01-01",
  "payment_terms": "Net 30",
  "company_name": "Your Company Ltd.",
  "company_address": "123 Business Street\nNew York, NY 10001\nUnited States",
  "company_tax_id": "US123456789",
  "company_email": "billing@yourcompany.com",
  "company_phone": "+1 (555) 123-4567",
  "client_name": "Client Company Inc.",
  "client_address": "456 Client Avenue\nLos Angeles, CA 90001\nUnited States",
  "client_email": "contact@client.com",
  "client_phone": "+1 (555) 987-6543",
  "currency": "USD",
  "payment_method": "Bank Transfer",
  "item_description": "Professional consulting services\nProject management and delivery",
  "quantity": "1",
  "unit_price": "5000.00",
  "tax_rate": "0",
  "discount": "0",
  "notes": "Thank you for your business!",
  "mark_paid": false,
  "format": "pdf"
}
```

**Required Fields:**

- `invoice_no`
- `invoice_date` (YYYY-MM-DD format)
- `due_date` (YYYY-MM-DD format)
- `company_name`
- `company_address`
- `client_name`
- `client_address`
- `currency`
- `item_description`
- `unit_price`

**Optional Fields:**

- `payment_terms` (default: "Net 30")
- `company_tax_id`
- `company_email`
- `company_phone`
- `client_email`
- `client_phone`
- `payment_method` (default: "Bank Transfer")
- `quantity` (default: "1")
- `tax_rate` (default: "0")
- `discount` (default: "0")
- `notes`
- `mark_paid` (default: false)
- `format` (default: "pdf", options: "pdf" or "png")

**Response:**

- Returns the generated invoice file as a download
- Content-Type: `application/pdf` or `image/png`
- Filename format: `invoice_{invoice_no}_{timestamp}.{pdf|png}`

**Error Responses:**

```json
// 401 Unauthorized
{
  "detail": "Invalid API key"
}

// 500 Internal Server Error
{
  "detail": "Error generating invoice: {error message}"
}
```

---

## Example Usage

### cURL

```bash
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-secret-api-key" \
  -d '{
    "invoice_no": "2025-55577",
    "invoice_date": "2025-12-02",
    "due_date": "2026-01-01",
    "company_name": "Your Company Ltd.",
    "company_address": "123 Business Street\nNew York, NY 10001",
    "client_name": "Client Company Inc.",
    "client_address": "456 Client Avenue\nLos Angeles, CA 90001",
    "currency": "USD",
    "item_description": "Consulting services",
    "unit_price": "5000.00",
    "format": "pdf"
  }' \
  --output invoice.pdf
```

### Python

```python
import requests

API_URL = "http://localhost:8000/api/generate"
API_KEY = "your-secret-api-key"

invoice_data = {
    "invoice_no": "2025-55577",
    "invoice_date": "2025-12-02",
    "due_date": "2026-01-01",
    "company_name": "Your Company Ltd.",
    "company_address": "123 Business Street\nNew York, NY 10001",
    "client_name": "Client Company Inc.",
    "client_address": "456 Client Avenue\nLos Angeles, CA 90001",
    "currency": "USD",
    "item_description": "Consulting services",
    "unit_price": "5000.00",
    "format": "pdf"
}

response = requests.post(
    API_URL,
    json=invoice_data,
    headers={"X-API-Key": API_KEY}
)

if response.status_code == 200:
    with open("invoice.pdf", "wb") as f:
        f.write(response.content)
    print("Invoice generated successfully!")
else:
    print(f"Error: {response.json()}")
```

### JavaScript (Fetch)

```javascript
const API_URL = "http://localhost:8000/api/generate";
const API_KEY = "your-secret-api-key";

const invoiceData = {
  invoice_no: "2025-55577",
  invoice_date: "2025-12-02",
  due_date: "2026-01-01",
  company_name: "Your Company Ltd.",
  company_address: "123 Business Street\nNew York, NY 10001",
  client_name: "Client Company Inc.",
  client_address: "456 Client Avenue\nLos Angeles, CA 90001",
  currency: "USD",
  item_description: "Consulting services",
  unit_price: "5000.00",
  format: "pdf",
};

fetch(API_URL, {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    "X-API-Key": API_KEY,
  },
  body: JSON.stringify(invoiceData),
})
  .then((response) => response.blob())
  .then((blob) => {
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "invoice.pdf";
    a.click();
  })
  .catch((error) => console.error("Error:", error));
```

---

## CORS

The API supports CORS to allow requests from frontend applications. In production, you should configure specific allowed origins in the CORS middleware.

---

## Interactive API Documentation

Once the server is running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
