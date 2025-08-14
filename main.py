from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, StreamingResponse
import io, datetime
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
from imagegen import draw_receipt_png_bytes

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
      .card{{max-width:720px;margin:0 auto;background:#fff;padding:24px;border-radius:12px;border:1px solid #e5e7eb}}
      h1{{margin:0 0 16px;font-size:22px}}
      label{{display:block;margin-top:12px;color:#334155;font-size:14px}}
      input{{width:100%;padding:10px 12px;margin-top:6px;border:1px solid #cbd5e1;border-radius:8px;font-size:14px}}
      button{{margin-top:18px;padding:10px 14px;border-radius:8px;border:1px solid #0ea5e9;background:#0284c7;color:#fff;font-weight:600;cursor:pointer}}
      small{{color:#64748b}}
    </style>
  </head>
  <body>
    <div class="card">
      <h1>Paid Receipt Generator</h1>
      <form method="post" action="/generate">
        <label>Company Name
          <input name="company_name" value="Your Company Name" required />
        </label>
        <label>Receipt No.
          <input name="receipt_no" value="INV-2025-001" required />
        </label>
        <label>Received From
          <input name="received_from" value="Client/Company" required />
        </label>
        <label>Receipt Date <small>e.g. 15 May 2024</small>
          <input name="receipt_date" value="{datetime.date.today().strftime("%d %b %Y")}" required />
        </label>
        <label>Currency
          <input name="currency" value="USD" required />
        </label>
        <label>Total Amount
          <input name="totalsum" value="1000.50" required />
        </label>
        <label>Description
          <input name="description" value="Service payment" required />
        </label>
        <button type="submit">Generate PNG</button>
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
    company_name: str = Form(...),
    receipt_no: str = Form(...),
    received_from: str = Form(...),
    receipt_date: str = Form(...),
    currency: str = Form(...),
    totalsum: str = Form(...),
    description: str = Form(...),
):
    png = draw_receipt_png_bytes(company_name, receipt_no, received_from,
                                 receipt_date, currency, totalsum, description)
    filename = f"receipt_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.png"
    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
    return StreamingResponse(io.BytesIO(png), media_type="image/png", headers=headers)
