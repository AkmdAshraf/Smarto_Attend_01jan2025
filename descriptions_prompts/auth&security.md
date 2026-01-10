Here are comprehensive prompts with code for implementing Authentication & Security using your anti-gravity framework:

## **PROMPT 1: COMPREHENSIVE AUTHENTICATION SYSTEM**

```python
"""
IMPLEMENT A COMPREHETE AUTHENTICATION & AUTHORIZATION SYSTEM WITH ANTI-GRAVITY LOGGING

REQUIREMENTS:
1. User roles: Admin (full access), Teacher (view/add students), Viewer (view only)
2. Secure password hashing with bcrypt/scrypt
3. Session management with Flask-Session
4. Login/Logout functionality with protected routes
5. Password reset with email verification
6. Brute force protection (5 failed attempts locks account for 15 min)
7. Session timeout (30 minutes inactivity)
8. Remember Me functionality
9. User management interface (CRUD operations)
10. Activity logging for all authentication events

IMPLEMENTATION DETAILS:
- Create users.json with schema: {username: {password_hash, role, email, created_at, last_login, failed_attempts, locked_until}}
- Use @login_required decorator with role parameter
- Add @antigravity_trace to ALL authentication functions
- Use @track_runtime_value for password hashing and session operations
- Implement password policy: min 12 chars, uppercase, lowercase, number, special char
- Add CSRF protection for all forms
- Create login.html, register.html, forgot_password.html, reset_password.html templates
- Add user profile page with password change functionality

ROUTES TO CREATE:
- GET/POST /login
- GET/POST /register
- GET/POST /forgot_password
- GET/POST /reset_password/<token>
- GET /logout
- GET/POST /profile
- GET/POST /change_password
- GET /users (admin only)
- GET/POST /users/add (admin only)
- GET/POST /users/edit/<username> (admin only)
- GET /users/delete/<username> (admin only)

USE EXISTING ANTI-GRAVITY PATTERNS:
- @antigravity_trace for all route handlers and auth functions
- @track_runtime_value for performance-critical operations
- Maintain consistent error handling and flash messages

SECURITY FEATURES:
- Password hashing with werkzeug.security or bcrypt
- Secure session cookies (HttpOnly, Secure, SameSite=Strict)
- Rate limiting on login attempts
- Input validation and sanitization
- Log all authentication attempts (success/fail)
- Session fixation prevention
"""

# AUTHENTICATION CODE TO ADD TO YOUR app.py
import os
import json
import time
import uuid
from datetime import datetime, timedelta
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session, Response, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from logger_config import antigravity_trace, track_runtime_value

# ==================== AUTHENTICATION CONFIGURATION ====================
USERS_FILE = os.path.join(BASE_DIR, 'users.json')
SESSION_TIMEOUT = 1800  # 30 minutes in seconds
MAX_FAILED_ATTEMPTS = 5
LOCKOUT_DURATION = 900  # 15 minutes in seconds

# ==================== USER MANAGEMENT FUNCTIONS ====================
@antigravity_trace
def load_users():
    """Load users from JSON file with anti-gravity tracing"""
    if not os.path.exists(USERS_FILE):
        # Create default admin user
        default_users = {
            "admin": {
                "password_hash": generate_password_hash("Admin@123"),
                "role": "admin",
                "email": "admin@school.edu",
                "created_at": datetime.now().isoformat(),
                "last_login": None,
                "failed_attempts": 0,
                "locked_until": None,
                "is_active": True,
                "last_password_change": datetime.now().isoformat()
            }
        }
        save_users(default_users)
        return default_users
    try:
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error loading users: {e}")
        return {}

@antigravity_trace
def save_users(users_data):
    """Save users to JSON file with anti-gravity tracing"""
    try:
        with open(USERS_FILE, 'w') as f:
            json.dump(users_data, f, indent=4, default=str)
    except IOError as e:
        print(f"Error saving users: {e}")
        raise

@antigravity_trace
def create_user(username, password, email, role="viewer"):
    """Create new user with validation and anti-gravity tracing"""
    users = load_users()
    
    if username in users:
        return False, "Username already exists"
    
    # Validate password strength
    is_valid, msg = validate_password(password)
    if not is_valid:
        return False, msg
    
    # Hash password with performance tracking
    @track_runtime_value(operation="password_hashing")
    def hash_password(pwd):
        return generate_password_hash(pwd, method='scrypt')
    
    password_hash = hash_password(password)
    
    users[username] = {
        "password_hash": password_hash,
        "role": role,
        "email": email,
        "created_at": datetime.now().isoformat(),
        "last_login": None,
        "failed_attempts": 0,
        "locked_until": None,
        "is_active": True,
        "last_password_change": datetime.now().isoformat()
    }
    
    save_users(users)
    return True, "User created successfully"

@antigravity_trace
def validate_password(password):
    """Validate password strength"""
    if len(password) < 12:
        return False, "Password must be at least 12 characters long"
    
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(not c.isalnum() for c in password)
    
    if not (has_upper and has_lower and has_digit and has_special):
        return False, "Password must contain uppercase, lowercase, digit, and special character"
    
    return True, "Password is valid"

# ==================== AUTHENTICATION DECORATORS ====================
def login_required(f):
    """Decorator to require login for routes"""
    @wraps(f)
    @antigravity_trace
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please login to access this page", "error")
            return redirect(url_for('login', next=request.url))
        
        # Check session timeout
        last_activity = session.get('last_activity')
        if last_activity:
            last_activity_time = datetime.fromisoformat(last_activity)
            if datetime.now() - last_activity_time > timedelta(seconds=SESSION_TIMEOUT):
                flash("Session expired. Please login again.", "error")
                session.clear()
                return redirect(url_for('login'))
        
        # Update last activity
        session['last_activity'] = datetime.now().isoformat()
        
        return f(*args, **kwargs)
    return decorated_function

def role_required(*roles):
    """Decorator to require specific role(s)"""
    def decorator(f):
        @wraps(f)
        @antigravity_trace
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash("Please login to access this page", "error")
                return redirect(url_for('login', next=request.url))
            
            user_role = session.get('user_role')
            if user_role not in roles and user_role != 'admin':
                flash("You don't have permission to access this page", "error")
                return redirect(url_for('dashboard'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# ==================== AUTHENTICATION ROUTES ====================
@app.route("/login", methods=["GET", "POST"])
@antigravity_trace
def login():
    """Login route with anti-gravity tracing"""
    # If already logged in, redirect to dashboard
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember_me = request.form.get('remember_me') == 'on'
        
        # Load users with performance tracking
        @track_runtime_value(operation="load_users")
        def load_users_wrapper():
            return load_users()
        
        users = load_users_wrapper()
        
        # Check if user exists and is not locked
        if username not in users:
            flash("Invalid username or password", "error")
            return render_template('login.html')
        
        user = users[username]
        
        # Check if account is locked
        if user.get('locked_until'):
            locked_until = datetime.fromisoformat(user['locked_until'])
            if datetime.now() < locked_until:
                remaining = (locked_until - datetime.now()).seconds // 60
                flash(f"Account locked. Try again in {remaining} minutes", "error")
                return render_template('login.html')
            else:
                # Unlock account
                user['locked_until'] = None
                user['failed_attempts'] = 0
        
        # Check if account is active
        if not user.get('is_active', True):
            flash("Account is deactivated. Contact administrator.", "error")
            return render_template('login.html')
        
        # Verify password with performance tracking
        @track_runtime_value(operation="password_verification")
        def verify_password(pwd_hash, pwd):
            return check_password_hash(pwd_hash, pwd)
        
        if verify_password(user['password_hash'], password):
            # Successful login
            session['user_id'] = username
            session['user_role'] = user['role']
            session['last_activity'] = datetime.now().isoformat()
            
            # Update user record
            user['last_login'] = datetime.now().isoformat()
            user['failed_attempts'] = 0
            user['locked_until'] = None
            
            # Set session permanence for remember me
            if remember_me:
                session.permanent = True
                app.permanent_session_lifetime = timedelta(days=30)
            else:
                session.permanent = False
            
            save_users(users)
            
            flash(f"Welcome back, {username}!", "success")
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard'))
        else:
            # Failed login
            user['failed_attempts'] = user.get('failed_attempts', 0) + 1
            
            if user['failed_attempts'] >= MAX_FAILED_ATTEMPTS:
                lock_until = datetime.now() + timedelta(seconds=LOCKOUT_DURATION)
                user['locked_until'] = lock_until.isoformat()
                flash(f"Account locked for {LOCKOUT_DURATION//60} minutes due to too many failed attempts", "error")
            else:
                remaining = MAX_FAILED_ATTEMPTS - user['failed_attempts']
                flash(f"Invalid password. {remaining} attempts remaining", "error")
            
            save_users(users)
    
    return render_template('login.html')

@app.route("/logout")
@antigravity_trace
def logout():
    """Logout route with anti-gravity tracing"""
    username = session.get('user_id', 'Unknown')
    session.clear()
    flash(f"Goodbye, {username}! You have been logged out.", "success")
    return redirect(url_for('login'))

@app.route("/register", methods=["GET", "POST"])
@antigravity_trace
def register():
    """User registration route with anti-gravity tracing"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Validate inputs
        if not username or not email or not password:
            flash("All fields are required", "error")
            return render_template('register.html')
        
        if password != confirm_password:
            flash("Passwords do not match", "error")
            return render_template('register.html')
        
        # Create user
        success, message = create_user(username, password, email, role="viewer")
        
        if success:
            flash(message, "success")
            return redirect(url_for('login'))
        else:
            flash(message, "error")
    
    return render_template('register.html')

@app.route("/forgot_password", methods=["GET", "POST"])
@antigravity_trace
def forgot_password():
    """Forgot password route with anti-gravity tracing"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        
        users = load_users()
        
        # Find user by email
        user_found = None
        for username, user_data in users.items():
            if user_data.get('email') == email:
                user_found = username
                break
        
        if user_found:
            # Generate reset token (in real app, send email)
            token = str(uuid.uuid4())
            users[user_found]['reset_token'] = token
            users[user_found]['reset_token_expiry'] = (datetime.now() + timedelta(hours=1)).isoformat()
            save_users(users)
            
            # In production, send email with reset link
            reset_url = url_for('reset_password', token=token, _external=True)
            flash(f"Password reset link has been generated. In production, this would be emailed.", "info")
            flash(f"Reset URL: {reset_url}", "info")
        else:
            flash("If an account exists with that email, a reset link will be sent.", "info")
        
        return redirect(url_for('login'))
    
    return render_template('forgot_password.html')

@app.route("/reset_password/<token>", methods=["GET", "POST"])
@antigravity_trace
def reset_password(token):
    """Reset password route with anti-gravity tracing"""
    users = load_users()
    
    # Find user with valid token
    user_found = None
    for username, user_data in users.items():
        user_token = user_data.get('reset_token')
        token_expiry = user_data.get('reset_token_expiry')
        
        if user_token == token and token_expiry:
            expiry_time = datetime.fromisoformat(token_expiry)
            if datetime.now() < expiry_time:
                user_found = username
                break
    
    if not user_found:
        flash("Invalid or expired reset token", "error")
        return redirect(url_for('forgot_password'))
    
    if request.method == 'POST':
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        if password != confirm_password:
            flash("Passwords do not match", "error")
            return render_template('reset_password.html', token=token)
        
        # Validate password strength
        is_valid, msg = validate_password(password)
        if not is_valid:
            flash(msg, "error")
            return render_template('reset_password.html', token=token)
        
        # Update password
        users[user_found]['password_hash'] = generate_password_hash(password, method='scrypt')
        users[user_found]['last_password_change'] = datetime.now().isoformat()
        users[user_found].pop('reset_token', None)
        users[user_found].pop('reset_token_expiry', None)
        
        save_users(users)
        
        flash("Password reset successfully! Please login with your new password.", "success")
        return redirect(url_for('login'))
    
    return render_template('reset_password.html', token=token)

@app.route("/profile")
@login_required
@antigravity_trace
def profile():
    """User profile page with anti-gravity tracing"""
    users = load_users()
    user_data = users.get(session['user_id'], {})
    
    # Remove sensitive data
    profile_data = {
        'username': session['user_id'],
        'role': session['user_role'],
        'email': user_data.get('email', ''),
        'created_at': user_data.get('created_at', ''),
        'last_login': user_data.get('last_login', ''),
        'last_password_change': user_data.get('last_password_change', '')
    }
    
    return render_template('profile.html', user=profile_data)

@app.route("/change_password", methods=["GET", "POST"])
@login_required
@antigravity_trace
def change_password():
    """Change password route with anti-gravity tracing"""
    if request.method == 'POST':
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        users = load_users()
        user = users.get(session['user_id'])
        
        if not user:
            flash("User not found", "error")
            return redirect(url_for('profile'))
        
        # Verify current password
        if not check_password_hash(user['password_hash'], current_password):
            flash("Current password is incorrect", "error")
            return redirect(url_for('change_password'))
        
        if new_password != confirm_password:
            flash("New passwords do not match", "error")
            return redirect(url_for('change_password'))
        
        # Validate new password
        is_valid, msg = validate_password(new_password)
        if not is_valid:
            flash(msg, "error")
            return redirect(url_for('change_password'))
        
        # Update password
        user['password_hash'] = generate_password_hash(new_password, method='scrypt')
        user['last_password_change'] = datetime.now().isoformat()
        
        save_users(users)
        
        flash("Password changed successfully!", "success")
        return redirect(url_for('profile'))
    
    return render_template('change_password.html')

# ==================== ADMIN USER MANAGEMENT ROUTES ====================
@app.route("/users")
@login_required
@role_required('admin')
@antigravity_trace
def manage_users():
    """User management page (admin only)"""
    users = load_users()
    
    # Prepare user list without password hashes
    user_list = []
    for username, data in users.items():
        user_list.append({
            'username': username,
            'role': data.get('role', 'viewer'),
            'email': data.get('email', ''),
            'created_at': data.get('created_at', ''),
            'last_login': data.get('last_login', ''),
            'is_active': data.get('is_active', True),
            'failed_attempts': data.get('failed_attempts', 0)
        })
    
    return render_template('users.html', users=user_list)

@app.route("/users/add", methods=["GET", "POST"])
@login_required
@role_required('admin')
@antigravity_trace
def add_user():
    """Add new user (admin only)"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        role = request.form.get('role', 'viewer')
        
        success, message = create_user(username, password, email, role)
        
        if success:
            flash(message, "success")
            return redirect(url_for('manage_users'))
        else:
            flash(message, "error")
    
    return render_template('add_user.html')

@app.route("/users/edit/<username>", methods=["GET", "POST"])
@login_required
@role_required('admin')
@antigravity_trace
def edit_user(username):
    """Edit user (admin only)"""
    users = load_users()
    
    if username not in users:
        flash("User not found", "error")
        return redirect(url_for('manage_users'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        role = request.form.get('role', 'viewer')
        is_active = request.form.get('is_active') == 'on'
        
        users[username]['email'] = email
        users[username]['role'] = role
        users[username]['is_active'] = is_active
        
        # If deactivating, clear any locks
        if not is_active:
            users[username]['locked_until'] = None
            users[username]['failed_attempts'] = 0
        
        save_users(users)
        
        flash(f"User {username} updated successfully", "success")
        return redirect(url_for('manage_users'))
    
    return render_template('edit_user.html', user=users[username], username=username)

@app.route("/users/delete/<username>")
@login_required
@role_required('admin')
@antigravity_trace
def delete_user(username):
    """Delete user (admin only)"""
    if username == session['user_id']:
        flash("You cannot delete your own account", "error")
        return redirect(url_for('manage_users'))
    
    users = load_users()
    
    if username in users:
        del users[username]
        save_users(users)
        flash(f"User {username} deleted successfully", "success")
    else:
        flash("User not found", "error")
    
    return redirect(url_for('manage_users'))

@app.route("/dashboard")
@login_required
@antigravity_trace
def dashboard():
    """Main dashboard page with anti-gravity tracing"""
    # Load statistics
    students = load_students()
    attendance = load_attendance()
    
    # Calculate stats
    today = datetime.now().strftime("%Y-%m-%d")
    present_today = 0
    
    for roll_no, data in attendance.items():
        if 'entry' in data:
            present_today += 1
    
    stats = {
        'total_students': len(students),
        'present_today': present_today,
        'absent_today': len(students) - present_today,
        'attendance_rate': (present_today / len(students) * 100) if students else 0
    }
    
    return render_template('dashboard.html', stats=stats, user_role=session.get('user_role'))

# ==================== UPDATE EXISTING ROUTES WITH AUTH ====================
# Example of protecting existing routes:

@app.route("/add_student", methods=["GET", "POST"])
@login_required
@role_required('admin', 'teacher')
@antigravity_trace
def add_student_protected():
    # Your existing add_student logic here
    pass

@app.route("/students")
@login_required
@antigravity_trace
def students_protected():
    # Your existing students logic here
    pass

@app.route("/delete_student/<roll_no>")
@login_required
@role_required('admin')
@antigravity_trace
def delete_student_protected(roll_no):
    # Your existing delete_student logic here
    pass

@app.route("/train")
@login_required
@role_required('admin')
@antigravity_trace
def train_model_protected():
    # Your existing train logic here
    pass

@app.route("/export")
@login_required
@role_required('admin', 'teacher')
@antigravity_trace
def export_protected():
    # Your existing export logic here
    pass

# Update the home route to redirect to dashboard if logged in
@app.route("/")
@antigravity_trace
def home():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template("home.html")
```

## **PROMPT 2: SECURITY HARDENING IMPLEMENTATION**

```python
"""
IMPLEMENT COMPREHENSIVE SECURITY HARDENING WITH ANTI-GRAVITY MONITORING

REQUIREMENTS:
1. CSRF Protection for all forms
2. Secure HTTP Headers (CSP, HSTS, X-Frame-Options)
3. Input Validation & Sanitization
4. Rate Limiting for sensitive endpoints
5. SQL Injection Prevention patterns
6. XSS Protection
7. File Upload Security
8. Security Headers Configuration
9. Security Logging with @antigravity_trace
10. Regular Security Audits

IMPLEMENTATION DETAILS:
- Use Flask-SeaSurf or Flask-WTF for CSRF protection
- Implement custom security headers middleware
- Add input validation decorators
- Create rate limiting with Flask-Limiter
- Implement file upload validation
- Add security event logging
- Create security dashboard for monitoring

SECURITY FEATURES TO ADD:
1. CSRF tokens on all forms
2. Content Security Policy
3. HTTP Strict Transport Security
4. X-Content-Type-Options: nosniff
5. X-Frame-Options: DENY
6. Referrer-Policy: strict-origin-when-cross-origin
7. Input validation for all user inputs
8. Rate limiting: 100/hour for login, 1000/hour for general
9. File type validation for uploads
10. Secure session configuration

USE ANTI-GRAVITY FOR:
- @antigravity_trace for all security events
- @track_runtime_value for security operations
- Log all security violations
- Monitor rate limit hits
- Track failed authentication attempts
"""

# SECURITY CODE TO ADD TO YOUR app.py
from flask import Flask, render_template, request, redirect, url_for, flash, session, Response, jsonify
from flask_talisman import Talisman
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from functools import wraps
import bleach
import re

# ==================== SECURITY CONFIGURATION ====================
# Initialize Talisman for security headers
csp = {
    'default-src': '\'self\'',
    'style-src': ['\'self\'', '\'unsafe-inline\'', 'https://cdn.jsdelivr.net'],
    'script-src': ['\'self\'', '\'unsafe-inline\'', 'https://cdn.jsdelivr.net'],
    'img-src': ['\'self\'', 'data:', 'blob:'],
    'font-src': ['\'self\'', 'https://cdn.jsdelivr.net']
}

talisman = Talisman(
    app,
    content_security_policy=csp,
    content_security_policy_nonce_in=['script-src'],
    force_https=False,  # Set to True in production
    strict_transport_security=True,
    strict_transport_security_max_age=31536000,
    frame_options='DENY',
    referrer_policy='strict-origin-when-cross-origin',
    feature_policy={
        'geolocation': '\'none\'',
        'camera': '\'self\'',  # Allow camera for face capture
        'microphone': '\'none\''
    }
)

# Initialize rate limiter
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["1000 per hour", "100 per minute"],
    storage_uri="memory://",
    strategy="fixed-window"
)

# ==================== SECURITY DECORATORS ====================
def validate_input(*validators):
    """Decorator to validate and sanitize input"""
    def decorator(f):
        @wraps(f)
        @antigravity_trace
        def decorated_function(*args, **kwargs):
            if request.method in ['POST', 'PUT', 'PATCH']:
                for field, validator in validators:
                    value = request.form.get(field) or request.json.get(field) if request.is_json else None
                    if value:
                        is_valid, message = validator(value)
                        if not is_valid:
                            flash(f"Invalid input for {field}: {message}", "error")
                            return redirect(request.referrer or url_for('home'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def sanitize_input(data):
    """Sanitize input data to prevent XSS"""
    if isinstance(data, str):
        # Allow basic HTML tags for rich text if needed
        allowed_tags = ['b', 'i', 'u', 'em', 'strong', 'p', 'br']
        return bleach.clean(data, tags=allowed_tags, strip=True)
    elif isinstance(data, dict):
        return {k: sanitize_input(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [sanitize_input(item) for item in data]
    return data

# ==================== INPUT VALIDATORS ====================
@track_runtime_value(operation="input_validation")
def validate_username(username):
    """Validate username format"""
    if not 3 <= len(username) <= 50:
        return False, "Username must be between 3 and 50 characters"
    
    if not re.match(r'^[a-zA-Z0-9_\-\.]+$', username):
        return False, "Username can only contain letters, numbers, dots, hyphens and underscores"
    
    return True, "Valid username"

@track_runtime_value(operation="input_validation")
def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return False, "Invalid email format"
    
    return True, "Valid email"

@track_runtime_value(operation="input_validation")
def validate_roll_no(roll_no):
    """Validate roll number format"""
    if not roll_no:
        return False, "Roll number is required"
    
    if not re.match(r'^[A-Za-z0-9_\-]+$', roll_no):
        return False, "Roll number can only contain letters, numbers, hyphens and underscores"
    
    return True, "Valid roll number"

@track_runtime_value(operation="input_validation")
def validate_name(name):
    """Validate name format"""
    if not name:
        return False, "Name is required"
    
    if len(name) > 100:
        return False, "Name too long (max 100 characters)"
    
    # Allow letters, spaces, hyphens, and apostrophes
    if not re.match(r'^[A-Za-z\s\-\'\.]+$', name):
        return False, "Name can only contain letters, spaces, hyphens, apostrophes and dots"
    
    return True, "Valid name"

# ==================== SECURITY MIDDLEWARE ====================
@app.before_request
@antigravity_trace
def security_checks():
    """Perform security checks before each request"""
    # Skip for static files
    if request.endpoint and 'static' in request.endpoint:
        return
    
    # Log security events
    security_log = {
        'timestamp': datetime.now().isoformat(),
        'ip': request.remote_addr,
        'method': request.method,
        'endpoint': request.endpoint,
        'user_agent': request.user_agent.string[:200],
        'user_id': session.get('user_id', 'anonymous')
    }
    
    # Check for suspicious headers
    suspicious_headers = ['X-Forwarded-Host', 'X-Original-URL', 'X-Rewrite-URL']
    for header in suspicious_headers:
        if header in request.headers:
            security_log['suspicious_header'] = header
            # Log but don't block in development
    
    # Input sanitization for form data
    if request.method in ['POST', 'PUT', 'PATCH']:
        if request.form:
            for key in list(request.form.keys()):
                if isinstance(request.form[key], str):
                    # Create mutable copy
                    form_data = request.form.to_dict()
                    form_data[key] = sanitize_input(form_data[key])
                    request.form = ImmutableMultiDict(form_data)
    
    # Store in app context for logging
    app.security_log = security_log

@app.after_request
@antigravity_trace
def add_security_headers(response):
    """Add security headers to responses"""
    # Additional custom headers
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    
    # Remove server header
    if 'Server' in response.headers:
        del response.headers['Server']
    
    # Log response security
    if hasattr(app, 'security_log'):
        app.security_log['response_status'] = response.status_code
        app.security_log['response_size'] = len(response.get_data())
        
        # Log to anti-gravity
        print(f"Security Event: {json.dumps(app.security_log)}")
    
    return response

# ==================== RATE LIMITED ENDPOINTS ====================
@app.route("/login", methods=["GET", "POST"])
@limiter.limit("10 per minute")
@antigravity_trace
def login_rate_limited():
    """Login with rate limiting"""
    # Your existing login code here
    pass

@app.route("/register", methods=["GET", "POST"])
@limiter.limit("5 per hour")
@antigravity_trace
def register_rate_limited():
    """Register with rate limiting"""
    # Your existing register code here
    pass

@app.route("/forgot_password", methods=["GET", "POST"])
@limiter.limit("5 per hour")
@antigravity_trace
def forgot_password_rate_limited():
    """Forgot password with rate limiting"""
    # Your existing forgot_password code here
    pass

# ==================== FILE UPLOAD SECURITY ====================
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

@track_runtime_value(operation="file_validation")
def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@track_runtime_value(operation="file_validation")
def validate_uploaded_file(file):
    """Validate uploaded file for security"""
    if not file:
        return False, "No file uploaded"
    
    if file.filename == '':
        return False, "No file selected"
    
    if not allowed_file(file.filename):
        return False, f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
    
    # Check file size
    file.seek(0, 2)  # Seek to end
    file_size = file.tell()
    file.seek(0)  # Seek back to start
    
    if file_size > MAX_FILE_SIZE:
        return False, f"File too large. Maximum size: {MAX_FILE_SIZE//1024//1024}MB"
    
    # Check file header (magic numbers)
    file_header = file.read(4)
    file.seek(0)
    
    # JPEG: FF D8 FF E0/E1/E2/E3/E8/DB
    # PNG: 89 50 4E 47
    if file_header.startswith(b'\xff\xd8\xff'):
        expected_extension = 'jpg'
    elif file_header.startswith(b'\x89PNG'):
        expected_extension = 'png'
    elif file_header.startswith(b'GIF8'):
        expected_extension = 'gif'
    else:
        return False, "Invalid file format"
    
    # Verify extension matches content
    actual_extension = file.filename.rsplit('.', 1)[1].lower()
    if expected_extension != actual_extension:
        return False, f"File extension mismatch. Expected: {expected_extension}"
    
    return True, "File is valid"

# ==================== SECURITY DASHBOARD ====================
@app.route("/security/logs")
@login_required
@role_required('admin')
@antigravity_trace
def security_logs():
    """View security logs (admin only)"""
    log_file = os.path.join(BASE_DIR, 'security.log')
    
    if not os.path.exists(log_file):
        return render_template('security_logs.html', logs=["No security logs found"])
    
    try:
        with open(log_file, 'r') as f:
            logs = f.readlines()[-100:]  # Last 100 lines
        return render_template('security_logs.html', logs=logs)
    except Exception as e:
        flash(f"Error reading security logs: {e}", "error")
        return render_template('security_logs.html', logs=[])
```

## **PROMPT 3: TEMPLATES FOR AUTHENTICATION & SECURITY**

```
CREATE THE FOLLOWING TEMPLATE FILES FOR AUTHENTICATION:

1. templates/login.html
2. templates/register.html
3. templates/forgot_password.html
4. templates/reset_password.html
5. templates/profile.html
6. templates/change