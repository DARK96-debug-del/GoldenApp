from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Baza yaratish
def init_db():
    if not os.path.exists('database.db'):
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        ''')
        conn.commit()
        conn.close()

init_db()

# Bosh sahifa
@app.route('/')
def index():
    if 'username' in session:
        return render_template('home.html', username=session['username'])
    return redirect(url_for('login'))

# Ro'yxatdan o'tish
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not username.startswith('@'):
            flash('Username @ bilan boshlanishi kerak!', 'error')
            return redirect(url_for('register'))

        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        try:
            c.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
            conn.commit()
            flash('Muvaffaqiyatli ro‘yxatdan o‘tildi!', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Bu username allaqachon mavjud!', 'error')
            return redirect(url_for('register'))
        finally:
            conn.close()

    return render_template('register.html')

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
        user = c.fetchone()
        conn.close()

        if user:
            session['username'] = username
            flash('Muvaffaqiyatli kirildi!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Login yoki parol xato!', 'error')
            return redirect(url_for('login'))

    return render_template('login.html')

# Logout
@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('Chiqildi.', 'info')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
