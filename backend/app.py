from flask import Flask, render_template, request, redirect, url_for, jsonify, flash, send_from_directory, session
import sqlite3
import bcrypt
import os
from dotenv import load_dotenv  # For loading the passkey from .env

# Initialize the Flask app
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this in production

# Specify the full path to your pass.env file
env_path = os.path.join('E:\\PBL Attendance\\backend\\pass.env')

# Load the pass.env file from the explicit path
load_dotenv(env_path)

# Fetch the ADMIN_PASSKEY
ADMIN_PASSKEY = os.getenv('ADMIN_PASSKEY', 'supersecretkey')

def init_db():
    db_folder = os.path.join('backend', 'database')
    os.makedirs(db_folder, exist_ok=True)
    db_path = os.path.join(db_folder, 'users.db')

    # Connect to the SQLite database and create the table with a role field
    with sqlite3.connect(db_path) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY, 
                username TEXT UNIQUE, 
                password TEXT,
                role TEXT DEFAULT 'student'  -- Default role is student
            )
        ''')
        conn.commit()

        # Check if the default admin exists, if not create it
        cursor = conn.cursor()
        cursor.execute('SELECT username FROM users WHERE username = "admin"')
        admin_exists = cursor.fetchone()

        if not admin_exists:
            # Insert the default admin with a hashed password and admin role
            hashed_password = bcrypt.hashpw("adminpass".encode('utf-8'), bcrypt.gensalt())  # Default password: adminpass
            conn.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)', 
                         ("admin", hashed_password, "admin"))
            conn.commit()

@app.route('/')
def index():
    # If the user is already logged in, redirect to the admin terminal
    if 'username' in session:
        return redirect(url_for('admin_dashboard'))
    return render_template('login.html')

# Route to serve images from the 'backend/asset/images' directory
@app.route('/images/<filename>')
def get_image(filename):
    # Adjust the path to the directory where your image is located
    image_dir = os.path.join(os.getcwd(), 'backend', 'asset', 'images')
    return send_from_directory(image_dir, filename)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        
        # If the user selected "Request Role Assignment", set role to "pending"
        if role == 'request':
            role = 'pending'

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Use the same db_path for the connection
        db_path = os.path.join('backend', 'database', 'users.db')
        with sqlite3.connect(db_path) as conn:
            try:
                # Insert the new user with the selected or pending role
                conn.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)', (username, hashed_password, role))
                conn.commit()

                # Return a JSON response
                return jsonify({'message': 'Registration successful! Please login'})

            except sqlite3.IntegrityError:
                # Handle the UNIQUE constraint error
                return jsonify({'message': 'Username already exists. Please choose another one.'}), 400

    return render_template('register.html')


@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    db_path = os.path.join('backend', 'database', 'users.db')
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT password, role FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()

        if user and bcrypt.checkpw(password.encode('utf-8'), user[0]):
            session['username'] = username
            session['role'] = user[1]

            # Ensure that session is flagged as modified
            session.modified = True

            # If the user is admin, redirect to passkey validation page and reset passkey validation session
            if user[1] == 'admin':
                session['passkey_validated'] = False  # Reset passkey validation
                session.modified = True  # Ensure session gets updated
                return jsonify({'message': 'passkey_required'})  # Return a response to JS to redirect
            else:
                return jsonify({'message': 'success'})  # Redirect for non-admin users
        else:
            flash('Invalid username or password', 'error')
            return jsonify({'message': 'error'})  # Return error message as JSON

@app.route('/passkey', methods=['GET', 'POST'])
def passkey_validation():
    if request.method == 'POST':
        passkey = request.form['passkey']
        
        # Compare the provided passkey with the stored passkey
        if passkey == ADMIN_PASSKEY:
            session['passkey_validated'] = True  # Set passkey validation to True
            session.modified = True  # Ensure session is updated
            # Redirect to the admin dashboard directly from the server
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid passkey!', 'error')
            return redirect(url_for('passkey_validation'))  # Reload the passkey page on failure
    
    return render_template('passkey.html')

@app.route('/admin_dashboard')
def admin_dashboard():
    print(session)  # Print the session to debug
    # Ensure the user is logged in as admin and has completed passkey validation
    if 'username' not in session or session.get('role') != 'admin':
        print("User is not logged in as admin")
        return redirect(url_for('index'))
    
    # Check if the admin has validated the passkey
    if not session.get('passkey_validated'):
        flash('You need to validate the passkey first.', 'error')
        print("Passkey not validated yet")
        return redirect(url_for('passkey_validation'))

    print("Admin dashboard accessed")
    return render_template('dashboard/admin.html')


@app.route('/logout')
def logout():
    session.clear()  # Clear the session on logout
    return redirect(url_for('index'))


@app.route('/assign_role', methods=['POST'])
def assign_role():
    if 'username' not in session or session.get('role') != 'admin':
        return "Unauthorized access", 403  # Only admin users can assign roles

    username = request.form['username']
    new_role = request.form['role']

    # Use the same db_path for the connection
    db_path = os.path.join('backend', 'database', 'users.db')
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET role = ? WHERE username = ?', (new_role, username))
        conn.commit()

    flash(f"Role of {username} updated to {new_role}", 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/get_users_pending_role')
def get_users_pending_role():
    # Use the same db_path for the connection
    db_path = os.path.join('backend', 'database', 'users.db')
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        # Fetch users who have the role 'pending'
        cursor.execute('SELECT username, role FROM users WHERE role = "pending"')
        users = cursor.fetchall()  # Fetch all users with 'pending' role
    return jsonify(users)  # Return users as JSON response

@app.route('/get_users')
def get_users():
    # Use the same db_path for the connection
    db_path = os.path.join('backend', 'database', 'users.db')
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        # Fetch all users and their current roles
        cursor.execute('SELECT username, role FROM users')
        users = cursor.fetchall()  # Fetch all users with their current roles
    return jsonify(users)  # Return users as JSON response


if __name__ == '__main__':
    init_db()  # Initialize the database
    app.run(debug=True)  # Enable debug mode
