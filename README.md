# MediQueue - Smart Hospital Queue Management System

MediQueue is a QR-based smart hospital queue management system developed using Flask and SQLite. It helps hospitals manage OPD queues digitally, generate tokens automatically, prioritize emergency patients, and provide department-wise doctor dashboards.

## Features
- QR-based patient registration
- Automatic department-wise token generation
- Emergency patient priority handling
- Estimated waiting time calculation
- Duplicate patient registration prevention
- Morning and evening slot limits
- Department-wise doctor login
- Call Next Patient system
- Admin dashboard with analytics
- Token status checking

## Technologies Used
- Python
- Flask
- SQLite
- HTML
- Tailwind CSS
- Pandas
- Matplotlib
- PyWebView

## How to Run

### Web Version

```bash
python app.py
```

Open in browser:

```text
http://127.0.0.1:5000
```

### GUI Version

```bash
python gui.py
```
## Mobile QR Testing

For mobile QR testing, run ngrok:

```bash
ngrok http 5000
python make_qr.py

### Admin GUI Version

```bash
python admin_gui.py

## Author
Purva Murai
Gouri Mundada
