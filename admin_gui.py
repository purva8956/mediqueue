import webview
import threading
from app import app

def run_flask():
    app.run(debug=False)

# Run Flask server
threading.Thread(target=run_flask).start()

# Open Admin Panel GUI
webview.create_window(
    "MediQueue Admin Panel",
    "http://127.0.0.1:5000/admin"
)

webview.start()