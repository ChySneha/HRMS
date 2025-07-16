from flask import Flask, render_template, request, redirect, session
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'hrms_secret_key'

def get_db():
    return sqlite3.connect('hrms.db')

def create_tables():
    con = get_db()
    cur = con.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        userid TEXT UNIQUE,
        password TEXT,
        name TEXT,
        fathername TEXT,
        dob TEXT,
        address TEXT,
        aadhar_no TEXT,
        pan_no TEXT,
        bank_account TEXT,
        ifsc TEXT,
        micr_core TEXT,
        joining_date TEXT
    )''')
    cur.execute('''CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        userid TEXT,
        date TEXT,
        time TEXT
    )''')
    con.commit()
    con.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = (
            request.form['userid'], request.form['password'], request.form['name'],
            request.form['fathername'], request.form['dob'], request.form['address'],
            request.form['aadhar_no'], request.form['pan_no'], request.form['bank_account'],
            request.form['ifsc'], request.form['micr_core'],
            request.form['joining_date']
        )
        con = get_db()
        cur = con.cursor()
        cur.execute('''INSERT INTO users 
            (userid, password, name, fathername, dob, address, aadhar_no, pan_no, bank_account,
            ifsc, micr_core, joining_date) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', data)
        con.commit()
        con.close()
        return redirect('/login')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        uid = request.form['userid']
        pwd = request.form['password']
        con = get_db()
        cur = con.cursor()
        cur.execute("SELECT * FROM users WHERE userid=? AND password=?", (uid, pwd))
        user = cur.fetchone()
        con.close()
        if user:
            session['user'] = uid
            return redirect('/dashboard')
        else:
            return "Invalid credentials"
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user' in session:
        uid = session['user']
        con = get_db()
        cur = con.cursor()
        cur.execute("SELECT * FROM users WHERE userid=?", (uid,))
        user = cur.fetchone()
        con.close()
        return render_template('dashboard.html', user=user)
    return redirect('/login')

@app.route('/attendance', methods=['GET', 'POST'])
def attendance():
    if 'user' not in session:
        return redirect('/login')
    if request.method == 'POST':
        now = datetime.now()
        con = get_db()
        cur = con.cursor()
        cur.execute("INSERT INTO attendance (userid, date, time) VALUES (?, ?, ?)",
                    (session['user'], now.strftime("%Y-%m-%d"), now.strftime("%H:%M:%S")))
        con.commit()
        con.close()
        return "Attendance marked!"
    return render_template('attendance.html')

@app.route('/hr_panel')
def hr_panel():
    con = get_db()
    cur = con.cursor()
    cur.execute("SELECT userid, name, joining_date FROM users")
    users = cur.fetchall()
    return render_template('hr_panel.html', users=users)

# 🛠 Create tables on first run
create_tables()

# 🚀 Start the app
if __name__ == '__main__':
    app.run(debug=True)
