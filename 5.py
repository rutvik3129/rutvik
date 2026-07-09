import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
# Replace this with a secure random key in production
app.secret_key = os.environ.get('SECRET_KEY', 'shiv_clinic_secure_fallback_key')
DB_FILE = 'clinic.db'

def init_db():
    """Initializes the database and creates the appointments table if it doesn't exist."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS appointments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fullname TEXT NOT NULL,
                phone TEXT NOT NULL,
                preferred_date TEXT NOT NULL,
                service TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()

# Ensure the database structure is ready upon startup
init_db()

@app.route('/')
def home():
    """Renders the main clinic page."""
    return render_template('index.html')

@app.route('/book-appointment', methods=['POST'])
def book_appointment():
    """Handles submission of the appointment request form."""
    # 1. Retrieve and sanitize form data
    fullname = request.form.get('fullname', '').strip()
    phone = request.form.get('phone', '').strip()
    preferred_date = request.form.get('date', '').strip()
    service = request.form.get('service', '').strip()

    # 2. Server-side Validation
    if not fullname or not phone or not preferred_date or not service:
        flash("All fields are required. Please check your submission.", "error")
        return redirect(url_for('home') + '#appointment')

    # 3. Database Insertion (Using Parameterized Queries against SQL Injection)
    try:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO appointments (fullname, phone, preferred_date, service)
                VALUES (?, ?, ?, ?)
            ''', (fullname, phone, preferred_date, service))
            conn.commit()
        
        # Success Notification
        flash(f"Thank you, {fullname}! Your request for a {service} on {preferred_date} has been submitted successfully. Our team will call you at {phone} shortly.", "success")
    except Exception as e:
        # Log error in server console
        print(f"Database Error: {e}")
        flash("An internal error occurred while scheduling your appointment. Please try again later.", "error")

    # Redirect back to the appointment anchor section of the page
    return redirect(url_for('home') + '#appointment')

if __name__ == '__main__':
    # Runs local development server on http://127.0.0.1:5000
    app.run(host='127.0.0.1', port=5000, debug=True)