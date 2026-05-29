from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime

app = Flask(__name__)

QR_SECRET = "hospital2026"

# 1. Configuration (Wait times per department)
DEPT_TIMES = {
    "General Medicine": 15,
    "Cardiology": 30,
    "Pediatrics": 20,
    "Orthopedic": 20,
    "ENT": 15
}

MORNING_LIMITS = {
    "General Medicine": 20,
    "Cardiology": 10,
    "Pediatrics": 15,
    "Orthopedic": 12,
    "ENT": 8
}
EVENING_LIMITS = {
    "General Medicine": 25,
    "Cardiology": 2,
    "Pediatrics": 18,
    "Orthopedic": 15,
    "ENT": 10
}

DEPARTMENT_PASSWORDS = {
    "General Medicine": "gen123",
    "Cardiology": "cardio123",
    "Pediatrics": "pedia123",
    "Orthopedic": "ortho123",
    "ENT": "ent123"
}

def get_current_slot():

    current_hour = datetime.now().hour

    # Morning Slot
    if 9 <= current_hour < 14:
        return "Morning"

    # Evening Slot
    elif 16 <= current_hour < 24:
        return "Evening"

    # Closed Time
    else:
        return "Closed"
# 2. Database Setup
def init_db():
    conn = sqlite3.connect('hospital.db') 
    cursor = conn.cursor()
    cursor.execute('''
CREATE TABLE IF NOT EXISTS patients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    age INTEGER,
    department TEXT,
    token TEXT,
    is_emergency TEXT,
    reg_time TEXT,
    status TEXT,
    visit_date TEXT
)
''')

    conn.commit()
    conn.close()

# Initialize database
init_db()

# 3. Token Generation Logic
def generate_token_id(department):

    department = department.strip()

    conn = sqlite3.connect('hospital.db')
    cursor = conn.cursor()

    dept_prefix = {
        "General Medicine": "G",
        "Cardiology": "C",
        "Pediatrics": "P",
        "Orthopedic": "O",
        "ENT": "E"
    }

    prefix = dept_prefix.get(department, "X")

    cursor.execute("""
        SELECT COUNT(*) FROM patients
        WHERE department=?
    """, (department,))

    count = cursor.fetchone()[0]

    conn.close()

    return f"{prefix}-{101 + count}"

# 4. Home Route
@app.route('/')
def index():
    return render_template('index.html')




# 5. Registration Route
@app.route('/registration/<key>', methods=['GET', 'POST'])
def registration(key):

    if key != QR_SECRET:
        return "<h1>Access Denied. Please scan hospital QR code.</h1>"

    if request.method == 'GET':
        return render_template('registration.html')

    # Get form data
    p_name = (request.form.get('name') or '').strip()
    p_age = (request.form.get('age') or '').strip()
    p_dept = (request.form.get('dept') or '').strip()
    p_emer_type = (request.form.get('emergency_type') or '').strip()

    # Validation
    if not p_name or not p_name.replace(" ", "").isalpha():
        return "<h1>Error: Name must contain only alphabets.</h1>", 400

    if not p_age.isdigit() or int(p_age) <= 0:
        return "<h1>Error: Age must be a positive whole number.</h1>", 400

    if not p_dept or p_dept not in DEPT_TIMES:
        return "<h1>Error: Valid department selection is required.</h1>", 400

    # Emergency check
    is_critical = p_emer_type in [
        'Heart Attack',
        'Accident',
        'Severe Bleeding'
    ]

    # Slot checking system
    current_slot = get_current_slot()

    if (not is_critical) and current_slot == "Closed":
        return f"""
        <html>
        <head>
            <title>Hospital Closed</title>
            <script src="https://cdn.tailwindcss.com"></script>
            <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap" rel="stylesheet">
        </head>

        <body class="min-h-screen flex items-center justify-center bg-slate-100 p-4"
              style="font-family: 'Poppins', sans-serif;">

            <div class="bg-white rounded-3xl shadow-xl p-7 max-w-md w-full">

                <div class="text-center">
                    <div class="w-20 h-20 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
                        <span class="text-4xl">🏥</span>
                    </div>

                    <h1 class="text-3xl font-bold text-slate-800">
                        OPD Closed
                    </h1>

                    <p class="text-slate-500 mt-2">
                        Registration is currently unavailable.
                    </p>
                </div>

                <div class="mt-6 bg-slate-50 rounded-2xl p-5">
                    <h2 class="font-semibold text-slate-700 mb-4">
                        OPD Timings
                    </h2>

                    <div class="flex justify-between mb-3">
                        <span class="text-slate-600">Morning</span>
                        <span class="font-semibold">9 AM - 2 PM</span>
                    </div>

                    <div class="flex justify-between">
                        <span class="text-slate-600">Evening</span>
                        <span class="font-semibold">4 PM - 12 AM</span>
                    </div>
                </div>

                <div class="mt-5 border rounded-2xl p-5">
                    <h2 class="font-semibold text-slate-700 mb-4">
                        Your Details
                    </h2>

                    <div class="space-y-3">
                        <div class="flex justify-between">
                            <span class="text-slate-500">Name</span>
                            <span class="font-medium">{p_name}</span>
                        </div>

                        <div class="flex justify-between">
                            <span class="text-slate-500">Department</span>
                            <span class="font-medium">{p_dept}</span>
                        </div>

                        <div class="flex justify-between">
                            <span class="text-slate-500">Expected Wait</span>
                            <span class="font-medium text-blue-600">
                                Approx 2 Hours
                            </span>
                        </div>
                    </div>
                </div>

                <div class="mt-5 bg-yellow-50 border border-yellow-200 rounded-2xl p-4">
                    <div class="flex items-center gap-3">
                        <div class="w-3 h-3 bg-yellow-500 rounded-full"></div>

                        <div>
                            <h3 class="font-semibold text-yellow-700">
                                Doctor Busy
                            </h3>

                            <p class="text-sm text-slate-600">
                                Doctor is currently attending patients.
                            </p>
                        </div>
                    </div>
                </div>

                <div class="mt-6">
                    <a href="/"
                       class="block text-center bg-blue-600 text-white py-3 rounded-2xl font-semibold hover:bg-blue-700">
                        Back to Home
                    </a>
                </div>

            </div>
        </body>
        </html>
        """

    conn = sqlite3.connect('hospital.db')
    cursor = conn.cursor()

    today_date = datetime.now().strftime("%Y-%m-%d")

# ==============================
# DUPLICATE PATIENT CHECK
# ==============================

    cursor.execute("""
        SELECT token FROM patients
        WHERE lower(name)=lower(?)
                   
        AND age=?
        AND department=?
        AND visit_date=?
    """, (
        p_name,
        int(p_age),
        p_dept,
        today_date
    ))

    existing_patient = cursor.fetchone()

    if existing_patient:
        old_token = existing_patient[0]
        conn.close()

        return f"""
        <html>
        <head>
            <script src="https://cdn.tailwindcss.com"></script>
        </head>

        <body class="bg-slate-100 flex items-center justify-center min-h-screen">

            <div class="bg-white p-8 rounded-3xl shadow-xl text-center max-w-md">
                <h1 class="text-2xl font-bold text-red-600 mb-4">
                    Patient Already Registered
                </h1>

                <p class="text-slate-600 mb-5">
                    A token is already generated for this patient today.
                </p>

                <div class="bg-blue-50 p-5 rounded-2xl mb-5">
                    <p><b>Name:</b> {p_name}</p>
                    <p><b>Age:</b> {p_age}</p>
                    <p><b>Department:</b> {p_dept}</p>
                    <p><b>Existing Token:</b> {old_token}</p>
                </div>

                <a href="/"
                   class="bg-blue-600 text-white px-6 py-3 rounded-xl font-semibold">
                   Back to Home
                </a>
            </div>

        </body>
        </html>
        """

# ==============================
# SLOT LIMIT CHECK
# ==============================

    if not is_critical:
        cursor.execute("""
            SELECT COUNT(*) FROM patients
            WHERE department=?
            AND visit_date=?
            AND is_emergency='No'
        """, (
            p_dept,
            today_date
        ))

        patient_count = cursor.fetchone()[0]

        if current_slot == "Morning":
             department_limit = MORNING_LIMITS.get(p_dept, 10)
        elif current_slot == "Evening":
             department_limit = EVENING_LIMITS.get(p_dept, 10)
        else:
              department_limit = 0

        if current_slot in ["Morning", "Evening"] and patient_count >= department_limit:
           conn.close()

           return f"""
          <html>
    <head>
        <script src="https://cdn.tailwindcss.com"></script>
        </head>

         <body class="bg-slate-100 flex items-center justify-center min-h-screen">

        <div class="bg-white p-8 rounded-3xl shadow-xl text-center max-w-md">

            <h1 class="text-2xl font-bold text-red-600 mb-4">
                {current_slot} Slot Full
            </h1>

            <p class="text-slate-600 mb-5">
                Today's {current_slot.lower()} slot for <b>{p_dept}</b> is full. for <b>{p_dept}</b> is full.
            </p>

            <p class="text-slate-500 mb-4">
                Maximum limit: <b>{department_limit}</b> patients
            </p>

            <p class="text-slate-500 mb-6">
                Please visit in the evening slot: <b>4 PM - 12 AM</b>
            </p>

            <a href="/"
               class="bg-blue-600 text-white px-6 py-3 rounded-xl font-semibold">
               Back to Home
            </a>

        </div>

         </body>
         </html>
          """

# ==============================
# EMERGENCY + WAIT TIME LOGIC
# ==============================

    if is_critical:
        total_wait_time = 0
        patients_ahead = 0
        display_msg = "PRIORITY ENTRY: Please proceed to the ER immediately!"
    else:
        cursor.execute("""
            SELECT COUNT(*) FROM patients
            WHERE department=?
            AND is_emergency='No'
            AND visit_date=?
        """, (
            p_dept,
            today_date
        ))

        patients_ahead = cursor.fetchone()[0]
        total_wait_time = patients_ahead * DEPT_TIMES.get(p_dept, 15)
        display_msg = f"Estimated wait: {total_wait_time} mins"

# ==============================
# TOKEN GENERATION + INSERT
# ==============================

    p_token = generate_token_id(p_dept)
    p_time = datetime.now().strftime("%H:%M")
    p_status = "Waiting"
    p_visit_date = today_date
    p_emer_status = 'Yes' if is_critical else 'No'

    cursor.execute("""
        INSERT INTO patients
        (name, age, department, token, is_emergency, reg_time, status, visit_date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        p_name,
        int(p_age),
        p_dept,
        p_token,
        p_emer_status,
        p_time,
        p_status,
        p_visit_date
    ))

    conn.commit()
    conn.close()

    return redirect(url_for(
        'token_page',
        token=p_token,
        wait_time=total_wait_time,
        ahead=patients_ahead,
        msg=display_msg,
        dept=p_dept,
        name=p_name
    ))


# 6. Token Page
@app.route('/token')
def token_page():

    token = request.args.get('token')
    wait_time = request.args.get('wait_time')
    ahead = request.args.get('ahead')
    msg = request.args.get('msg')
    patient_dept = request.args.get('dept')
    name = request.args.get('name')

    is_emergency = "Yes" if msg and msg.startswith("PRIORITY") else "No"

    conn = sqlite3.connect('hospital.db')
    cursor = conn.cursor()

    current_tokens = {}

    for department in DEPT_TIMES.keys():

        cursor.execute("""
            SELECT token FROM patients
            WHERE department=?
            AND status='Called'
            ORDER BY id DESC
            LIMIT 1
        """, (department,))

        result = cursor.fetchone()

        if result:
            current_tokens[department] = result[0]
        else:
            current_tokens[department] = "Waiting..."

    conn.close()

    return render_template(
        'token.html',
        token=token,
        wait_time=wait_time,
        ahead=ahead,
        msg=msg,
        dept=patient_dept,
        name=name,
        current_tokens=current_tokens,
        is_emergency=is_emergency
    )

# 7. Admin Dashboard
@app.route('/doctor_login', methods=['GET', 'POST'])
def doctor_login():

    if request.method == 'POST':

        department = request.form.get('department')
        password = request.form.get('password')

        if department in DEPARTMENT_PASSWORDS and DEPARTMENT_PASSWORDS[department] == password:
            return redirect(url_for('department_dashboard', dept=department))

        return """
        <h2 style="color:red; text-align:center; margin-top:50px;">
            Invalid department or password
        </h2>
        <p style="text-align:center;">
            <a href="/doctor_login">Try Again</a>
        </p>
        """

    return """
    <html>
    <head>
        <title>Doctor Login</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>

    <body class="bg-slate-100 min-h-screen flex items-center justify-center">

        <div class="bg-white p-8 rounded-3xl shadow-xl w-full max-w-md">

            <h1 class="text-3xl font-black text-slate-800 mb-6 text-center">
                Doctor Login
            </h1>

            <form method="POST" class="space-y-5">

                <div>
                    <label class="font-semibold text-slate-600">Department</label>

                    <select name="department"
                            class="w-full mt-2 p-3 border rounded-xl">
                        <option>General Medicine</option>
                        <option>Cardiology</option>
                        <option>Pediatrics</option>
                        <option>Orthopedic</option>
                        <option>ENT</option>
                    </select>
                </div>

                <div>
                    <label class="font-semibold text-slate-600">Password</label>

                    <input type="password"
                           name="password"
                           required
                           class="w-full mt-2 p-3 border rounded-xl">
                </div>

                <button type="submit"
                        class="w-full bg-blue-600 text-white py-3 rounded-xl font-bold hover:bg-blue-700">
                    Login
                </button>

            </form>

            <a href="/"
               class="block text-center mt-5 text-blue-600 font-semibold">
                Back to Home
            </a>

        </div>

    </body>
    </html>
    """
@app.route('/admin')
def admin_panel():

    conn = sqlite3.connect('hospital.db')

    cursor = conn.cursor()

    # Total patients
    cursor.execute("SELECT COUNT(*) FROM patients")
    total_patients = cursor.fetchone()[0]

# Emergency patients
    cursor.execute(
        "SELECT COUNT(*) FROM patients WHERE is_emergency='Yes'"
    )
    emergency_count = cursor.fetchone()[0]

# Department counts
    cursor.execute("""
        SELECT department, COUNT(*)
        FROM patients
        GROUP BY department
    """)
    dept_data = cursor.fetchall()
    
# Graph Data

# ==============================
# MODERN DONUT CHART
# ==============================

    departments = []
    counts = []

    for dept, count in dept_data:
        departments.append(dept)
        counts.append(count)

    # Create figure
    import pandas as pd

    plt.figure(figsize=(8, 8))

    # Create donut chart
    plt.pie(
        counts,
        labels=departments,
        autopct='%1.1f%%',
        startangle=90,
        wedgeprops={'width': 0.4},
        textprops={'fontsize': 12}
    )

    # Title
    plt.title(
        "Department Wise Patients",
        fontsize=18,
        fontweight='bold'
    )


    # Save graph
    plt.savefig(
        'static/department_graph.png',
        bbox_inches='tight',
        transparent=True
    )

    plt.close()

    # Patient table
    df = pd.read_sql_query(
        "SELECT * FROM patients ORDER BY id DESC",
        conn
    )

    dept_html = ""
     
    for dept, count in dept_data:
       dept_html += f"""
    <div class="bg-blue-100 p-4 rounded-2xl shadow">

    <h3 class="text-lg font-bold text-slate-700">
        {dept}
    </h3>

    <p class="text-3xl font-black text-blue-700">
        {count}
    </p>

</div>
    """
# ==============================
# CURRENT SERVING TOKENS
# ==============================

    current_tokens = {}

    for dept in DEPT_TIMES.keys():

        cursor.execute("""
            SELECT token FROM patients
            WHERE department=?
            AND status='Called'
            ORDER BY id DESC
            LIMIT 1
        """, (dept,))

        result = cursor.fetchone()

        if result:
            current_tokens[dept] = result[0]
        else:
            current_tokens[dept] = "Waiting..."
    conn.close()
    table_html = df.to_html(
    classes='table-auto w-full border-collapse text-sm',
    index=False,
    border=0
)

    html = f"""
    <html>


    <head>
        <title>MediQueue Dashboard</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>

table {{
    width: 100%;
    border-collapse: collapse;
    border-radius: 15px;
    overflow: hidden;
}}

th {{
    background: #2563eb;
    color: white;
    padding: 14px;
    text-align: left;
}}

td {{
    padding: 12px;
    border-bottom: 1px solid #e5e7eb;
}}

tr:nth-child(even) {{
    background-color: #f8fafc;
}}

tr:hover {{
    background-color: #dbeafe;
}}

</style>
     </head>
      
    <body class="bg-slate-100 p-8 font-Montserrat">


        <h1 class="text-4xl font-black text-times new roman-800 mb-8">
            MediQueue Dashboard
        </h1>


        <!-- Top Cards -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">

            <div class="bg-white p-6 rounded-3xl shadow-xl">
                <h2 class="text-xl font-bold text-times new roman-600">
                    Total Patients
                </h2>

                <p class="text-5xl font-black text-blue-700 mt-3">
                    {total_patients}
                </p>
            </div>

            <div class="bg-white p-6 rounded-3xl shadow-xl">
                <h2 class="text-xl font-bold text-slate-600">
                    Emergency Cases
                </h2>

                <p class="text-5xl font-black text-red-600 mt-3">
                    {emergency_count}
                </p>
            </div>

        </div>

        <!-- Department Stats -->
        <h2 class="text-2xl font-black text-Montserrat-800 mb-4">
            Department Queue
        </h2>

        <div class="grid grid-cols-2 md:grid-cols-3 gap-5 mb-10">
            {dept_html}
        </div>

        <!-- Department Graph -->

<div class="bg-white p-6 rounded-3xl shadow-xl mb-10">

    <h2 class="text-2xl font-black text-slate-800 mb-5">
        Department Analytics
    </h2>

    <img
        src="/static/department_graph.png"
        class="rounded-2xl shadow-lg w-full"
    >

</div>

        <!-- Live Queue Table -->
        <div class="bg-white p-6 rounded-3xl shadow-xl overflow-auto">

            <h2 class="text-2xl font-black text-slate-800 mb-5">
                Live Patient Queue
            </h2>

            {table_html}

        </div>

        <!-- Buttons -->
        <div class="mt-8 flex gap-5">
 
        <a href="/doctor_login"
   class="bg-green-600 text-white px-6 py-3 rounded-2xl font-bold shadow-lg hover:bg-green-700">
   Doctor Login
</a>
            <a href="/clear"
               class="bg-red-600 text-white px-6 py-3 rounded-2xl font-bold shadow-lg hover:bg-red-700">
               Clear History
            </a>

            <a href="/"
               class="bg-blue-600 text-white px-6 py-3 rounded-2xl font-bold shadow-lg hover:bg-blue-700">
               Home
            </a>

        </div>

    </body>

    </html>
    """
    return html
# ==============================
# CALL NEXT PATIENT
# ==============================

@app.route('/call_next/<dept>')
def call_next(dept):

    conn = sqlite3.connect('hospital.db')
    cursor = conn.cursor()

    # Find next waiting patient
    cursor.execute("""
        SELECT id FROM patients
        WHERE department=? AND status='Waiting'
        ORDER BY id ASC
        LIMIT 1
    """, (dept,)
    )

    patient = cursor.fetchone()

    if patient:

        patient_id = patient[0]

        # Update status
        cursor.execute("""
            UPDATE patients
            SET status='Called'
            WHERE id=?
        """, (patient_id,))

        conn.commit()

    conn.close()

    return redirect(url_for('department_dashboard', dept=dept))
@app.route('/department/<dept>')
def department_dashboard(dept):

    conn = sqlite3.connect('hospital.db')
    cursor = conn.cursor()

    # Total department patients
    cursor.execute(
        "SELECT COUNT(*) FROM patients WHERE department=?",
        (dept,)
    )
    total_patients = cursor.fetchone()[0]

    # Waiting patients
    cursor.execute(
        "SELECT COUNT(*) FROM patients WHERE department=? AND status='Waiting'",
        (dept,)
    )
    waiting_count = cursor.fetchone()[0]

    # Called patients
    cursor.execute(
        "SELECT COUNT(*) FROM patients WHERE department=? AND status='Called'",
        (dept,)
    )
    called_count = cursor.fetchone()[0]

    # Department patient table
    df = pd.read_sql_query(
        "SELECT id, name, age, token, is_emergency, reg_time, status FROM patients WHERE department=? ORDER BY id ASC",
        conn,
        params=(dept,)
    )

    conn.close()

    # Department graph
    labels = ["Waiting", "Called"]
    values = [waiting_count, called_count]

    plt.figure(figsize=(5, 5))

    if sum(values) > 0:
        plt.pie(
            values,
            labels=labels,
            autopct='%1.1f%%',
            startangle=90,
            wedgeprops={'width': 0.4},
            textprops={'fontsize': 11}
        )
    else:
        plt.text(0.5, 0.5, "No Data", ha='center', va='center', fontsize=16)
        plt.axis('off')

    plt.title(f"{dept} Patient Status", fontsize=14, fontweight='bold')
    plt.savefig("static/department_status_graph.png", bbox_inches='tight', transparent=True)
    plt.close()

    table_html = df.to_html(
        classes='table-auto w-full border-collapse text-sm',
        index=False,
        border=0
    )

    return f"""
    <html>
    <head>
        <meta http-equiv="refresh" content="5">
        <title>{dept} Dashboard</title>
        <script src="https://cdn.tailwindcss.com"></script>

        <style>
            table {{
                width: 100%;
                border-collapse: collapse;
            }}

            th {{
                background: #2563eb;
                color: white;
                padding: 12px;
                text-align: left;
            }}

            td {{
                padding: 12px;
                border-bottom: 1px solid #e5e7eb;
            }}

            tr:nth-child(even) {{
                background-color: #f8fafc;
            }}
        </style>
    </head>

    <body class="bg-slate-100 p-8 font-sans">

        <h1 class="text-4xl font-black text-slate-800 mb-8">
            {dept} Doctor Dashboard
        </h1>
          <p class="text-sm text-slate-500 mb-4">
    Auto-refreshing every 5 seconds
</p>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">

            <div class="bg-white p-6 rounded-3xl shadow-xl">
                <h2 class="text-slate-500 font-bold">Total Patients</h2>
                <p class="text-5xl font-black text-blue-700 mt-3">{total_patients}</p>
            </div>

            <div class="bg-white p-6 rounded-3xl shadow-xl">
                <h2 class="text-slate-500 font-bold">Waiting</h2>
                <p class="text-5xl font-black text-yellow-600 mt-3">{waiting_count}</p>
            </div>

            <div class="bg-white p-6 rounded-3xl shadow-xl">
                <h2 class="text-slate-500 font-bold">Called</h2>
                <p class="text-5xl font-black text-green-600 mt-3">{called_count}</p>
            </div>

        </div>

        <div class="bg-white p-6 rounded-3xl shadow-xl mb-8">

            <h2 class="text-2xl font-black text-slate-800 mb-5">
                Department Status Graph
            </h2>

            <img src="/static/department_status_graph.png"
                 class="w-full max-w-md mx-auto">

        </div>

        <div class="bg-white p-6 rounded-3xl shadow-xl mb-8">

            <div class="flex justify-between items-center mb-5">

                <h2 class="text-2xl font-black text-slate-800">
                    Patient Details
                </h2>

                <a href="/call_next/{dept}"
                   class="bg-green-600 text-white px-6 py-3 rounded-xl font-bold hover:bg-green-700">
                   Call Next Patient
                </a>

            </div>

            {table_html}

        </div>

        <div class="flex gap-4">

            <a href="/clear"
               class="bg-red-600 text-white px-6 py-3 rounded-xl font-bold hover:bg-red-700">
               Clear History
            </a>

            <a href="/"
               class="bg-blue-600 text-white px-6 py-3 rounded-xl font-bold hover:bg-blue-700">
               Home
            </a>

            <a href="/doctor_login"
               class="bg-slate-700 text-white px-6 py-3 rounded-xl font-bold hover:bg-slate-800">
               Logout
            </a>

        </div>

    </body>
    </html>
    """
#---------------
#check token
#---------------
@app.route('/check_token', methods=['GET', 'POST'])
def check_token():

    if request.method == 'POST':

        token = (request.form.get('token') or '').strip().upper()

        conn = sqlite3.connect('hospital.db')
        cursor = conn.cursor()

        cursor.execute("""
            SELECT name, department, status
            FROM patients
            WHERE token=?
        """, (token,))

        patient = cursor.fetchone()

        conn.close()

        if patient:
            name, department, status = patient

            return f"""
            <html>
            <head>
                <script src="https://cdn.tailwindcss.com"></script>
            </head>

            <body class="bg-slate-100 min-h-screen flex items-center justify-center">

                <div class="bg-white p-8 rounded-3xl shadow-xl text-center max-w-md">

                    <h1 class="text-3xl font-black text-slate-800 mb-4">
                        Token Status
                    </h1>

                    <p class="text-xl font-bold text-blue-600 mb-4">
                        {token}
                    </p>

                    <p><b>Name:</b> {name}</p>
                    <p><b>Department:</b> {department}</p>
                    <p><b>Status:</b> {status}</p>

                    <br>

                    <a href="/"
                       class="bg-blue-600 text-white px-6 py-3 rounded-xl font-bold">
                       Home
                    </a>

                </div>

            </body>
            </html>
            """

        return """
        <h2 style="text-align:center; margin-top:100px;">
            Token not found.
            <br><br>
            <a href="/check_token">Try Again</a>
        </h2>
        """

    return """
    <html>
    <head>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>

    <body class="bg-slate-100 min-h-screen flex items-center justify-center">

        <div class="bg-white p-8 rounded-3xl shadow-xl max-w-md w-full">

            <h1 class="text-3xl font-black text-slate-800 mb-5 text-center">
                Check Token Status
            </h1>

            <form method="POST">

                <input type="text"
                       name="token"
                       placeholder="Enter token e.g. G-101"
                       class="w-full p-4 border rounded-xl mb-5"
                       required>

                <button type="submit"
                        class="w-full bg-blue-600 text-white py-3 rounded-xl font-bold">
                    Check Status
                </button>

            </form>

            <a href="/"
               class="block text-center mt-5 text-blue-600 font-semibold">
               Back to Home
            </a>

        </div>

    </body>
    </html>
    """

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():

    if request.method == 'POST':
        password = request.form.get('password')

        if password == "admin123":
            return redirect('/admin')

        return "<h2>Wrong Password</h2><a href='/admin_login'>Try Again</a>"

    return """
    <html>
    <head><script src="https://cdn.tailwindcss.com"></script></head>
    <body class="bg-slate-100 min-h-screen flex items-center justify-center">
        <div class="bg-white p-8 rounded-3xl shadow-xl max-w-md w-full">
            <h1 class="text-3xl font-black mb-5 text-center">Admin Login</h1>

            <form method="POST">
                <input type="password" name="password"
                       placeholder="Enter admin password"
                       class="w-full p-4 border rounded-xl mb-5" required>

                <button class="w-full bg-blue-600 text-white py-3 rounded-xl font-bold">
                    Login
                </button>
            </form>

            <a href="/" class="block text-center mt-5 text-blue-600 font-semibold">
                Back to Home
            </a>
        </div>
    </body>
    </html>
    """
#clear the admin panel
@app.route('/clear', methods=['GET', 'POST'])
def clear_database():

    if request.method == 'POST':

        conn = sqlite3.connect('hospital.db')
        cursor = conn.cursor()

        # Delete all data
        cursor.execute("DELETE FROM patients")

        # Reset auto increment
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='patients'")

        conn.commit()
        conn.close()

        return """
        <html>

        <head>
            <script src="https://cdn.tailwindcss.com"></script>
        </head>

        <body class="bg-slate-100 flex items-center justify-center min-h-screen">

            <div class="bg-white p-8 rounded-3xl shadow-xl text-center">

                <h1 class="text-3xl font-bold text-green-600 mb-4">
                    ✅ History Cleared
                </h1>

                <p class="text-slate-600 mb-5">
                    Database reset successfully.
                </p>

                <a href="/admin"
                   class="bg-blue-600 text-white px-6 py-3 rounded-xl font-semibold">
                   Back to Dashboard
                </a>

            </div>

        </body>

        </html>
        """

    return """
    <html>

    <head>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>

    <body class="bg-slate-100 flex items-center justify-center min-h-screen">

        <div class="bg-white p-8 rounded-3xl shadow-xl text-center max-w-md">

            <h2 class="text-2xl font-bold text-red-600 mb-4">
                Delete All Patient History?
            </h2>

            <p class="text-slate-500 mb-6">
                This action cannot be undone.
            </p>

            <form method="POST">

                <button
                    type="submit"
                    class="bg-red-600 text-white px-6 py-3 rounded-xl font-semibold hover:bg-red-700"
                >
                    Clear Database
                </button>

            </form>

        </div>

    </body>

    </html>
    """

# 8. Run Flask App
if __name__ == '__main__':

    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )
    