"""
Quick Setup Script - Creates sample users for testing
Run this ONCE after installing the system
"""

import sqlite3
from werkzeug.security import generate_password_hash

def setup_sample_users():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    
    # Create users table if not exists
    cursor.execute('''CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL,
        full_name TEXT,
        email TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Sample users
    users = [
        ("admin", "admin123", "Admin", "Admin Kumar", "admin@hospital.com"),
        ("doctor1", "doc123", "Doctor", "Dr. Rajesh Kumar", "rajesh@hospital.com"),
        ("doctor2", "doc123", "Doctor", "Dr. Priya Sharma", "priya@hospital.com"),
        ("patient1", "pat123", "Patient", "Ravi Sundar", "ravi@gmail.com"),
        ("patient2", "pat123", "Patient", "Lakshmi Devi", "lakshmi@gmail.com"),
        ("patient3", "pat123", "Patient", "Vijay Kumar", "vijay@gmail.com"),
    ]
    
    created_count = 0
    existing_count = 0
    
    for username, password, role, full_name, email in users:
        try:
            hashed_password = generate_password_hash(password)
            cursor.execute(
                "INSERT INTO users(username, password, role, full_name, email) VALUES(?,?,?,?,?)",
                (username, hashed_password, role, full_name, email)
            )
            created_count += 1
            print(f"✅ Created: {role} - {username} (Password: {password})")
        except sqlite3.IntegrityError:
            existing_count += 1
            print(f"⚠️  Already exists: {username}")
    
    conn.commit()
    conn.close()
    
    print(f"\n{'='*50}")
    print(f"✅ Setup Complete!")
    print(f"   Created: {created_count} users")
    print(f"   Already existed: {existing_count} users")
    print(f"{'='*50}\n")
    
    print("🎯 Sample Login Credentials:")
    print("   Admin:    username: admin    | password: admin123")
    print("   Doctor 1: username: doctor1  | password: doc123")
    print("   Doctor 2: username: doctor2  | password: doc123")
    print("   Patient 1: username: patient1 | password: pat123")
    print("   Patient 2: username: patient2 | password: pat123")
    print("   Patient 3: username: patient3 | password: pat123")
    print(f"\n{'='*50}")
    print("Now run: python app.py")
    print(f"{'='*50}\n")

if __name__ == "__main__":
    print("\n🏥 Patient Treatment Forgery Detection System")
    print("📦 Quick Setup - Creating Sample Users\n")
    setup_sample_users()