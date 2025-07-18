from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Change this to a secure random string

DATABASE = "database/mpdc.db"

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/")
def login():
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def do_login():
    username = request.form["username"]
    password = request.form["password"]
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password)).fetchone()
    conn.close()
    if user:
        session["user_id"] = user["id"]
        session["username"] = user["username"]
        session["role"] = user["role"]
        return redirect(url_for("dashboard"))
    else:
        return render_template("login.html", error="Invalid credentials")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/dashboard")
def dashboard():
    if "username" not in session:
        return redirect(url_for("login"))

    conn = sqlite3.connect("database/mpdc.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM lands")
    records = cursor.fetchall()
    conn.close()

    lands = [
        {
            "id": row[0],
            "owner_name": row[1],
            "title_number": row[2],
            "lot_number": row[3],
            "area": row[4],
            "location": row[5],
            "zoning_type": row[6],
            "remarks": row[7],
            "date_encoded": row[8],
        } for row in records
    ]

    current_time = datetime.now().strftime("%B %d, %Y %I:%M %p")

    return render_template("dashboard.html", lands=lands)

@app.route('/add', methods=['GET', 'POST'])
def add():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        owner_name = request.form['owner_name']
        title_number = request.form['title_number']
        lot_number = request.form['lot_number']
        area = request.form['area']
        location = request.form['location']
        zoning_type = request.form['zoning_type']
        remarks = request.form['remarks']
        date_encoded = datetime.now().strftime("%Y-%m-%d")

        conn = sqlite3.connect("database/mpdc.db")
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO lands (owner_name, title_number, lot_number, area, location, zoning_type, remarks, date_encoded)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (owner_name, title_number, lot_number, area, location, zoning_type, remarks, date_encoded))
        conn.commit()
        conn.close()

        return redirect(url_for('dashboard'))

    return render_template('add.html')

# Edit existing land entry

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    conn = sqlite3.connect("database/mpdc.db")
    cursor = conn.cursor()
    if request.method == 'POST':
        # Get updated values from the form
        updated_values = (
            request.form['owner_name'],
            request.form['title_number'],
            request.form['lot_number'],
            request.form['area'],
            request.form['location'],
            request.form['zoning_type'],
            request.form['remarks'],
            id
        )
        cursor.execute("""
            UPDATE lands
            SET owner_name=?, title_number=?, lot_number=?, area=?, location=?, zoning_type=?, remarks=?
            WHERE id=?
        """, updated_values)
        conn.commit()
        conn.close()
        return redirect(url_for('dashboard'))

    # If GET: Load existing data to pre-fill the form
    cursor.execute("SELECT * FROM lands WHERE id=?", (id,))
    land = cursor.fetchone()
    conn.close()
    return render_template('edit.html', land=land)

# Delete existing entry

@app.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    conn = sqlite3.connect("database/mpdc.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM lands WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))


# You can add more routes below here like /add, /edit, /delete, /report, etc.

if __name__ == "__main__":
    print("🚀 Starting MPDC Land Title & Zoning Web App...")
    app.run(debug=True)