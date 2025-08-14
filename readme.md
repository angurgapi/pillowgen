# pillowgen — Payment Receipt Generator (FastAPI + Pillow)

Generate a **PAID** receipt PNG for OCR & automatch testing purpose from a tiny web form.  
No font installs, no database, no storage — just submit the form and download the image.

## ✨ Features
- Minimal form: **company_name, receipt_no, received_from, receipt_date, currency, totalsum, description**
- Always **PAID**, quantity fixed to **1**
- Renders a crisp PNG via **Pillow**
- **Zero-install fonts**: tries common system fonts (Arial/Helvetica/Liberation); otherwise falls back to Pillow’s built-in font
- Stateless: nothing is stored server-side

---

## 🚀 Quickstart (local)

Requirements: **Python 3.8+**

```bash
git clone git@github.com:angurgapi/pillowgen.git
cd pillowgen
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
