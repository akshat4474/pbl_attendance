from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3
import bcrypt
import os
import flash

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this in production

# Database initialization
def init_db():
    # Specify the database folder inside the backend directory
    db_folder = os.path.join('backend', 'database')  # Correct path
    # Create the database directory if it doesn't exist
    os.makedirs(db_folder, exist_ok=True)
    # Full path to the SQLite database file
    db_path = os.path.join(db_folder, 'users.db')
    
    # Connect to the SQLite database
    with sqlite3.connect(db_path) as conn:
        conn.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT)')
        conn.commit()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Use the same db_path for the connection
        db_path = os.path.join('backend', 'database', 'users.db')
        with sqlite3.connect(db_path) as conn:
            try:
                conn.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
                conn.commit()
                
                # Return a JSON response
                return jsonify({'message': 'Registration successful!'})
                
            except sqlite3.IntegrityError:
                # Handle the UNIQUE constraint error
                return jsonify({'message': 'Username already exists. Please choose another one.'}), 400
            
    return render_template('register.html')
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    # Use the same db_path for the connection
    db_path = os.path.join('backend', 'database', 'users.db')
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT password FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()

        if user and bcrypt.checkpw(password.encode('utf-8'), user[0].encode('utf-8')):
            flash('Login successful!', 'success')
            return 'success'  # Return success for AJAX request
        else:
            return 'Invalid username or password.'  # Return error message

@app.route('/dashboard')
def dashboard():
    return "Welcome to the dashboard!"  # Replace with actual dashboard HTML

if __name__ == '__main__':
    init_db()  # Initialize the database
    app.run(debug=True)  # Enable debug mode