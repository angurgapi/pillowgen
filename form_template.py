# form_template.py
import datetime


def get_invoice_form_html() -> str:
    """Returns the HTML form for invoice generation."""
    today = datetime.date.today()
    due_date = today + datetime.timedelta(days=30)
    
    return f"""
<!doctype html>
<html>
  <head>
    <meta charset="utf-8"/>
    <title>Invoice Generator</title>
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
      button{{margin-top:24px;padding:12px 24px;border-radius:8px;border:1px solid #0ea5e9;background:#0284c7;color:#fff;font-weight:600;cursor:pointer;font-size:15px;width:100%}}
      button:hover{{background:#0369a1}}
      small{{color:#64748b}}
      .subtitle{{color:#64748b;font-size:14px;margin-bottom:24px}}
      .header{{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:24px}}
      .paid-checkbox{{display:flex;align-items:center;gap:8px;padding:12px 16px;background:#f0fdf4;border:2px solid #86efac;border-radius:8px;cursor:pointer}}
      .paid-checkbox input{{width:auto;margin:0;cursor:pointer}}
      .paid-checkbox label{{margin:0;cursor:pointer;color:#15803d;font-weight:600}}
      
      /* Tablet and smaller */
      @media (max-width: 768px) {{
        body{{padding:16px}}
        .card{{padding:24px;border-radius:8px}}
        h1{{font-size:20px}}
        h2{{font-size:15px;margin:20px 0 10px}}
        .row{{grid-template-columns:1fr;gap:0}}
        .header{{flex-direction:column;gap:16px}}
        .paid-checkbox{{width:100%;justify-content:center}}
        button{{padding:14px 20px}}
      }}
      
      /* Mobile */
      @media (max-width: 480px) {{
        body{{padding:12px}}
        .card{{padding:16px;border-radius:8px}}
        h1{{font-size:18px}}
        h2{{font-size:14px;margin:16px 0 8px}}
        label{{margin-top:8px;font-size:13px}}
        input,textarea{{padding:8px 10px;font-size:13px}}
        textarea{{min-height:60px}}
        button{{padding:12px 16px;font-size:14px}}
        .paid-checkbox{{padding:10px 14px;font-size:13px}}
        .subtitle{{font-size:13px}}
      }}
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
            <input type="date" name="invoice_date" value="{today.strftime("%Y-%m-%d")}" required />
          </label>
        </div>
        <div class="row">
          <label>Due Date
            <input type="date" name="due_date" value="{due_date.strftime("%Y-%m-%d")}" required />
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
