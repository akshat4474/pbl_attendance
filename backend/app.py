from flask import Flask, render_template, request, redirect, url_for, jsonify, flash, send_from_directory, session
import sqlite3
import bcrypt
import os
from dotenv import load_dotenv  # For loading the passkey from .env
import random,string

def generate_student_id(length=8):
    """Generate a random student ID."""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

base_dir = os.getcwd()  # Get the current working directory
template_dir = os.path.join(base_dir, 'frontend', 'templates')
static_dir = os.path.join(base_dir, 'frontend', 'static')
# Initialize the Flask app
app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)

app.secret_key = os.urandom(24) #Random secret key for session management

# Database paths
users_db_path = os.path.join(base_dir, 'backend', 'database', 'users.db')
attendance_db_path = os.path.join(base_dir, 'backend', 'database', 'attendance.db')

# Specify the full path to your pass.env file
env_path = os.path.join(base_dir, 'backend', 'pass.env')

# Load the pass.env file from the explicit path
load_dotenv(env_path)

# Fetch admin credentials from the .env file
ADMIN_NAME = os.getenv('ADMIN_NAME', 'admin')
ADMIN_PASS = os.getenv('ADMIN_PASS', 'adminpass')
ADMIN_PASSKEY = os.getenv('ADMIN_PASSKEY')


def init_db():
    db_folder = os.path.join('backend', 'database')
    os.makedirs(db_folder, exist_ok=True)

    # Create or connect to users.db
    with sqlite3.connect(users_db_path) as conn:
        cursor = conn.cursor()

        # Create the users table with student_id and registration_no columns
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY, 
                username TEXT UNIQUE, 
                email TEXT,
                student_id TEXT UNIQUE,  -- Student ID is now unique
                program TEXT,
                registration_no TEXT,
                password TEXT,
                role TEXT DEFAULT 'student'
            )
        ''')

        # Create or modify the attendance table to include student_id
        with sqlite3.connect(attendance_db_path) as conn:
            cursor = conn.cursor()

            # Create the attendance table with student_id
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS attendance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id TEXT,  -- Reference to the student ID
                    date TEXT,
                    status TEXT,
                    description TEXT,
                    FOREIGN KEY (student_id) REFERENCES users(student_id)
                )
            ''')

            conn.commit()

    print("Database initialized")


@app.route('/')
def index():
    # If the user is already logged in, check their role and redirect accordingly
    if 'username' in session:
        if session['role'] == 'admin':
            return redirect(url_for('admin_dashboard'))
        elif session['role'] == 'student':
            return redirect(url_for('student_dashboard'))
    return render_template('login.html')

# Route to serve the student dashboard
@app.route('/student_dashboard')
def student_dashboard():
    if 'username' not in session:
        return redirect(url_for('index'))

    # Fetch profile information for the logged-in user from users.db
    with sqlite3.connect(users_db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT username, email, student_id, program, registration_no FROM users WHERE username = ?', (session['username'],))
        profile = cursor.fetchone()

    # If profile is not found, redirect to login
    if not profile:
        return redirect(url_for('index'))

    return render_template('dashboard/student.html', profile=profile)

@app.route('/submit_attendance_request', methods=['POST'])
def submit_attendance_request():
    if 'username' not in session:
        return redirect(url_for('index'))

    # Fetch student_id from the database using the username
    with sqlite3.connect(users_db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT student_id FROM users WHERE username = ?', (session['username'],))
        student_id = cursor.fetchone()

    if student_id is None:
        flash('User not found.', 'error')
        return redirect(url_for('student_dashboard'))

    student_id = student_id[0]
    date = request.form['date']
    description = request.form.get('description', None)
    status = "pending"  # Default status is pending when the request is submitted

    with sqlite3.connect(attendance_db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO attendance (student_id, date, status, description) VALUES (?, ?, ?, ?)',
                       (student_id, date, status, description))
        conn.commit()

    flash('Attendance request submitted!', 'success')
    return redirect(url_for('student_dashboard'))


@app.route('/attendance_report', methods=['GET'])
def attendance_report():
    if 'username' not in session:
        return redirect(url_for('index'))

    # Fetch student_id from the database using the username
    with sqlite3.connect(users_db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT student_id FROM users WHERE username = ?', (session['username'],))
        student_id = cursor.fetchone()

    if student_id is None:
        flash('User not found.', 'error')
        return redirect(url_for('student_dashboard'))

    student_id = student_id[0]

    # Fetch attendance data for the logged-in user
    with sqlite3.connect(attendance_db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT date, status, description FROM attendance WHERE student_id = ?', (student_id,))
        attendance = cursor.fetchall()

    print(f'Attendance data fetched for {student_id}: {attendance}')

    return jsonify(attendance)




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

        # Generate a unique student ID
        student_id = generate_student_id()

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Use the same db_path for the connection
        db_path = os.path.join('backend', 'database', 'users.db')
        with sqlite3.connect(db_path) as conn:
            try:
                # Insert the new user with the generated student ID
                conn.execute('INSERT INTO users (username, password, student_id, role) VALUES (?, ?, ?, ?)',
                             (username, hashed_password, student_id, role))
                conn.commit()

                return jsonify({'message': 'Registration successful! Please login'})

            except sqlite3.IntegrityError:
                return jsonify({'message': 'Username already exists. Please choose another one.'}), 400

    return render_template('register.html')


@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    # Check if the username is the admin
    if username == ADMIN_NAME:
        # Validate the password for admin user
        if password == ADMIN_PASS:
            session['username'] = username
            session['role'] = 'admin'
            session['passkey_validated'] = False  # Admin must validate passkey
            session.modified = True
            return jsonify({'message': 'passkey_required'})  # Redirect to passkey validation page
        else:
            flash('Invalid admin credentials', 'error')
            return jsonify({'message': 'error'})  # Return error for wrong admin credentials

    # For non-admin users, query the database
    db_path = os.path.join('backend', 'database', 'users.db')
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT password, role FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()

        if user and bcrypt.checkpw(password.encode('utf-8'), user[0]):
            session['username'] = username
            session['role'] = user[1]
            session.modified = True
            return jsonify({'message': 'success'})  # Successful login
        else:
            flash('Invalid username or password', 'error')
            return jsonify({'message': 'error'})  # Return error message

@app.route('/passkey', methods=['GET', 'POST'])
def passkey_validation():
    if request.method == 'POST':
        passkey = request.form['passkey']
        
        # Compare the provided passkey with the stored passkey
        if passkey == ADMIN_PASSKEY:
            session['passkey_validated'] = True  # Set passkey validation to True
            session.modified = True  # Ensure session is updated
            return redirect(url_for('admin_dashboard'))  # Redirect to admin dashboard
        else:
            flash('Invalid passkey!', 'error')
            return redirect(url_for('passkey_validation'))  # Reload the passkey page on failure
    
    return render_template('passkey.html')

@app.route('/update_profile', methods=['POST'])
def update_profile():
    if 'username' not in session:
        return redirect(url_for('index'))

    username = session['username']
    new_username = request.form['name']
    new_email = request.form['email']
    new_registration_no = request.form['registration_no']
    new_password = request.form['password']

    with sqlite3.connect(users_db_path) as conn:
        cursor = conn.cursor()

        # Update profile information
        cursor.execute('UPDATE users SET username = ?, email = ?, registration_no = ? WHERE username = ?',
                       (new_username, new_email, new_registration_no, username))

        # If password is provided, update it
        if new_password:
            hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
            cursor.execute('UPDATE users SET password = ? WHERE username = ?', (hashed_password, username))

        conn.commit()

    # Update session with the new username
    session['username'] = new_username

    flash('Profile updated successfully!', 'success')
    return redirect(url_for('student_dashboard'))


@app.route('/admin_dashboard')
def admin_dashboard():
    if 'username' not in session or session.get('role') != 'admin':
        return redirect(url_for('index'))
    
    if not session.get('passkey_validated'):
        flash('You need to validate the passkey first.', 'error')
        return redirect(url_for('passkey_validation'))

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

    # Prevent the admin from changing their own role
    if username == ADMIN_NAME:
        flash('You cannot change the admin role.', 'error')
        return redirect(url_for('admin_dashboard'))

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
    db_path = os.path.join('backend', 'database', 'users.db')
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT username, role FROM users')
        users = cursor.fetchall()  # Fetch all users with their current roles
    return jsonify(users)

if __name__ == '__main__':
    init_db()  # Initialize the database
    app.run(debug=True)  # Enable debug mode
