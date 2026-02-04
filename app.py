"""
🏥 PATIENT TREATMENT FORGERY DETECTION SYSTEM
==============================================
Flask-based web application with AI detection and Blockchain security
Author: Enhanced Medical System
Version: 2.0

Features:
- User authentication (Doctor/Patient/Admin)
- AI-powered prescription forgery detection
- Blockchain-secured medical records
- Real-time fraud monitoring
- Comprehensive analytics dashboard
"""

from flask import Flask, render_template, request, redirect, session, flash, send_from_directory
import sqlite3
import os
from datetime import datetime
from blockchain import add_record, verify_chain, get_chain_stats
from ai_detector import detect_forgery, get_detection_details
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "your_secret_key_change_in_production_2024"

# Configuration
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
    print(f"✅ Created uploads folder: {UPLOAD_FOLDER}")

# ========== HELPER FUNCTIONS ==========

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ========== DATABASE FUNCTIONS ==========

def get_db():
    """Connect to SQLite database with Row factory for dict-like access"""
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """
    Initialize database with all required tables
    - users: Store user accounts (Doctor/Patient/Admin)
    - treatments: Store prescription records with AI analysis
    """
    conn = get_db()
    
    print("📊 Initializing database...")
    
    # Users table
    conn.execute('''CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL,
        full_name TEXT,
        email TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Treatments table with AI analysis fields
    conn.execute('''CREATE TABLE IF NOT EXISTS treatments(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER,
        doctor_id INTEGER,
        disease TEXT,
        medicine TEXT,
        prescription_file TEXT,
        hash TEXT,
        status TEXT,
        confidence_score REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(patient_id) REFERENCES users(id),
        FOREIGN KEY(doctor_id) REFERENCES users(id)
    )''')
    
    conn.commit()
    conn.close()
    print("✅ Database initialized successfully")

# ========== AUTHENTICATION ROUTES ==========
    conn.close()

@app.route("/", methods=["GET","POST"])
def login():
    """
    🔐 User login page
    Supports: Doctor, Patient, Admin
    """
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        
        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
        conn.close()
        
        if user and check_password_hash(user['password'], password):
            # Set session
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            session['full_name'] = user['full_name']
            
            print(f"✅ Login successful: {username} ({user['role']})")
            flash(f"Welcome back, {user['full_name']}!", "success")
            
            # Redirect based on role
            if user['role'] == "Doctor":
                return redirect("/doctor")
            elif user['role'] == "Patient":
                return redirect("/patient")
            else:
                return redirect("/admin")
        else:
            print(f"❌ Login failed: {username}")
            flash("Invalid username or password", "error")
            return redirect("/")
    
    return render_template("login.html")

@app.route("/register", methods=["GET","POST"])
def register():
    """
    📝 User registration page
    Creates new accounts for Doctor/Patient/Admin
    """
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        role = request.form["role"]
        full_name = request.form["full_name"]
        email = request.form["email"]
        
        # Basic validation
        if len(password) < 4:
            flash("Password must be at least 4 characters long", "error")
            return redirect("/register")
        
        hashed_password = generate_password_hash(password)
        
        try:
            conn = get_db()
            conn.execute("INSERT INTO users(username, password, role, full_name, email) VALUES(?,?,?,?,?)",
                        (username, hashed_password, role, full_name, email))
            conn.commit()
            conn.close()
            
            print(f"✅ New user registered: {username} ({role})")
            flash(f"Registration successful! Welcome {full_name}. You can login now.", "success")
            return redirect("/")
        except sqlite3.IntegrityError:
            print(f"❌ Registration failed: Username '{username}' already exists")
            flash("Username already exists. Please choose another.", "error")
            return redirect("/register")
    
    return render_template("register.html")

@app.route("/logout")
def logout():
    """🚪 User logout - clears session"""
    username = session.get('username', 'Unknown')
    print(f"👋 Logout: {username}")
    session.clear()
    flash("You have been logged out successfully", "success")
    return redirect("/")

# ========== DOCTOR ROUTES ==========
@app.route("/doctor", methods=["GET","POST"])
def doctor():
    if 'user_id' not in session or session['role'] != "Doctor":
        return redirect("/")
    
    if request.method == "POST":
        patient_id = request.form.get("patient_id")
        disease = request.form["disease"]
        medicine = request.form["medicine"]
        file = request.files.get("prescription")
        
        # Validation
        if not patient_id or patient_id == "":
            flash("Please select a patient!", "error")
            conn = get_db()
            patients = conn.execute("SELECT id, username, full_name FROM users WHERE role='Patient'").fetchall()
            treatments = conn.execute("""SELECT t.*, u.username, u.full_name 
                                        FROM treatments t 
                                        JOIN users u ON t.patient_id = u.id 
                                        WHERE t.doctor_id = ? 
                                        ORDER BY t.created_at DESC""", 
                                     (session['user_id'],)).fetchall()
            conn.close()
            return render_template("doctor.html", treatments=treatments, patients=patients)
        
        if not file:
            flash("Please upload prescription image!", "error")
            conn = get_db()
            patients = conn.execute("SELECT id, username, full_name FROM users WHERE role='Patient'").fetchall()
            treatments = conn.execute("""SELECT t.*, u.username, u.full_name 
                                        FROM treatments t 
                                        JOIN users u ON t.patient_id = u.id 
                                        WHERE t.doctor_id = ? 
                                        ORDER BY t.created_at DESC""", 
                                     (session['user_id'],)).fetchall()
            conn.close()
            return render_template("doctor.html", treatments=treatments, patients=patients)
        
        # Save file
        from datetime import datetime
        filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        # AI Check
        result, confidence = detect_forgery(filepath)
        
        # Blockchain Save
        hash_value = add_record(patient_id, session['user_id'], f"{disease}|{medicine}")
        
        # Save in DB
        conn = get_db()
        conn.execute("INSERT INTO treatments(patient_id, doctor_id, disease, medicine, prescription_file, hash, status, confidence_score) VALUES(?,?,?,?,?,?,?,?)",
                     (patient_id, session['user_id'], disease, medicine, filename, hash_value, result, confidence))
        conn.commit()
        conn.close()
        
        flash(f"✅ Treatment saved! Status: {result} (Confidence: {confidence:.1f}%)", "success")
        return redirect("/doctor")
    
    # Get treatments and patients list
    conn = get_db()
    treatments = conn.execute("""SELECT t.*, u.username, u.full_name 
                                FROM treatments t 
                                JOIN users u ON t.patient_id = u.id 
                                WHERE t.doctor_id = ? 
                                ORDER BY t.created_at DESC""", 
                             (session['user_id'],)).fetchall()
    
    # Get all patients for dropdown
    patients = conn.execute("SELECT id, username, full_name FROM users WHERE role='Patient'").fetchall()
    conn.close()
    
    return render_template("doctor.html", treatments=treatments, patients=patients)

# Patient Dashboard
@app.route("/patient")
def patient():
    if 'user_id' not in session or session['role'] != "Patient":
        return redirect("/")
    
    conn = get_db()
    treatments = conn.execute("""SELECT t.*, u.full_name as doctor_name 
                                FROM treatments t 
                                JOIN users u ON t.doctor_id = u.id 
                                WHERE t.patient_id = ? 
                                ORDER BY t.created_at DESC""", 
                             (session['user_id'],)).fetchall()
    conn.close()
    
    return render_template("patient.html", treatments=treatments)

# Admin Dashboard
@app.route("/admin")
def admin():
    if 'user_id' not in session or session['role'] != "Admin":
        return redirect("/")
    
    conn = get_db()
    frauds = conn.execute("""SELECT t.*, 
                            p.full_name as patient_name,
                            d.full_name as doctor_name
                            FROM treatments t 
                            JOIN users p ON t.patient_id = p.id
                            JOIN users d ON t.doctor_id = d.id
                            WHERE t.status='Fake' 
                            ORDER BY t.created_at DESC""").fetchall()
    conn.close()
    
    return render_template("admin.html", frauds=frauds)

# Verify Blockchain
@app.route("/verify_blockchain")
def verify_blockchain():
    is_valid = verify_chain()
    if is_valid:
        flash("✅ Blockchain is valid and secure!", "success")
    else:
        flash("⚠️ Blockchain integrity compromised!", "error")
    
    return redirect(request.referrer or "/")

if __name__ == "__main__":
    init_db()
    app.run(debug=True)