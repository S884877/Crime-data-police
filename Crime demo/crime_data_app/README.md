# Crime Data Analysis (Flask)

Minimal scaffold for a Crime Data Analysis web app.

Quick start:

1. Create a virtualenv and install deps:

```bash
python -m venv venv
# Windows PowerShell
venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Run app:

```bash
python app.py
```

3. Open http://127.0.0.1:5000

Features:
- Upload CSV datasets (expects columns like `crime_type`, `location`, `year`).
- REST API endpoints in `app.py` for upload and summary.
- Frontend in `templates/index.html` using Chart.js (via CDN).

Next steps: add server-side listing of uploaded files, more robust validation, and extra charts.
