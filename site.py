import os
from flask import Flask, request, redirect, url_for, render_template, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from models import db, User, ClassificationResult
from dotenv import load_dotenv
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import numpy as np
from PIL import Image
import smtplib
from email.mime.text import MIMEText
import re

# Initialize Flask app
app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Load environment variables
load_dotenv()

# Secret key setup
app.secret_key = os.getenv('SECRET_KEY') or 'fallback_secret_key'

# Database Config
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'instance', 'app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Upload folders
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
PROCESSED_FOLDER = os.path.join(BASE_DIR, 'static', 'processed')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER

# ML Model
model_path = os.path.join(BASE_DIR, 'model', '/Users/yashpatil/Downloads/Modern-Login-master/fake_logo_detector (2).h5')
model = load_model(model_path)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Classification Logic
def classify_logo(filepath, processed_filename, model, app):
    try:
        img = image.load_img(filepath, target_size=(150, 150))
        img_tensor = image.img_to_array(img)
        img_tensor = np.expand_dims(img_tensor, axis=0)
        img_tensor = img_tensor.astype("float32") / 255.0

        processed_img_array = (img_tensor[0] * 255).astype(np.uint8)
        processed_img = Image.fromarray(processed_img_array)

        processed_folder = app.config['PROCESSED_FOLDER']
        os.makedirs(processed_folder, exist_ok=True)
        processed_path = os.path.join(processed_folder, processed_filename)
        processed_img.save(processed_path)

        prediction = model.predict(img_tensor)[0][0]
        result = '✅ Real Logo' if prediction >= 0.5 else '❌ Fake Logo'
        color = 'blue' if prediction >= 0.5 else 'red'
        confidence = round(prediction * 100, 2)

        return result, confidence, processed_path, color

    except Exception as e:
        print("[ERROR classify_logo]:", e)
        return "⚠️ Error", 0, None, "gray"


# Create DB
with app.app_context():
    db.create_all()


# ---------------- ROUTES ---------------- #

@app.route('/')
def home():
    return render_template('index.html')


# Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name').strip()
        email = request.form.get('email').strip()
        password = request.form.get('password').strip()

        # Validate empty fields
        if not name or not email or not password:
            flash("All fields are required!", "error")
            return redirect(url_for('register'))

        # Validate name length
        if len(name) < 3:
            flash("Name must be at least 3 characters long!", "error")
            return redirect(url_for('register'))

        # Validate email format
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            flash("Invalid email format!", "error")
            return redirect(url_for('register'))

        # ✔ CHECK IF USER ALREADY EXISTS
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("User already exists!", "error")
            return redirect(url_for('register'))

        # Validate password strength
        if len(password) < 6:
            flash("Password must be at least 6 characters long!", "error")
            return redirect(url_for('register'))

        if not re.search(r'[A-Za-z]', password) or not re.search(r'[0-9]', password):
            flash("Password must contain letters AND numbers!", "error")
            return redirect(url_for('register'))

        # Save new user
        hashed_password = generate_password_hash(password)
        new_user = User(name=name, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful! Please log in.", "success")
        return redirect(url_for('register'))

    return render_template('register.html')


# Login
@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')

    user = User.query.filter_by(email=email).first()

    if user and check_password_hash(user.password, password):
        session['user_id'] = user.id
        return redirect(url_for('user_page', user_id=user.id))

    flash("Invalid credentials!", "error")
    return redirect(url_for('register'))

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')

        user = User.query.filter_by(email=email).first()
        if not user:
            flash("No user found with this email!", "error")
            return redirect(url_for('forgot_password'))

        # Generate token
        from itsdangerous import URLSafeTimedSerializer
        s = URLSafeTimedSerializer(app.secret_key)
        token = s.dumps(email, salt='reset-password')

        reset_url = url_for('reset_password', token=token, _external=True)

        #  OPTION 1: SHOW THE URL ON SCREEN INSTEAD OF SENDING EMAIL
        flash(f"Reset Link (testing): {reset_url}", "info")

        return redirect(url_for('forgot_password'))

    return render_template('forgot_password.html')

@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
    s = URLSafeTimedSerializer(app.secret_key)

    try:
        email = s.loads(token, salt='reset-password', max_age=3600)  # 1 hour
    except SignatureExpired:
        return "The link expired!"
    except BadSignature:
        return "Invalid reset link!"

    if request.method == 'POST':
        new_password = request.form.get('password')

        if len(new_password) < 6:
            flash("Password must be at least 6 characters!", "error")
            return redirect(request.url)

        hashed = generate_password_hash(new_password)
        user = User.query.filter_by(email=email).first()
        user.password = hashed
        db.session.commit()

        flash("Password reset successfully!", "success")
        return redirect(url_for('register'))

    return render_template('reset_password.html')
 


# USER PAGE
@app.route('/user_page/<int:user_id>', methods=['GET', 'POST'])
def user_page(user_id):
    user = User.query.get_or_404(user_id)
    classification_result = None
    uploaded_image_url = None
    processed_image_url = None
    confidence_score = None
    logo_status = None
    color = "gray"

    if request.method == 'POST':
        file = request.files.get('logo_image')
        if not file or file.filename == '':
            flash('No file uploaded!', 'error')
            return redirect(request.url)

        if allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            uploaded_image_url = url_for('static', filename='uploads/' + filename)
            processed_filename = f"processed_{filename}"

            logo_status, confidence_score, processed_path, color = classify_logo(
                filepath, processed_filename, model, app
            )

            classification_result = True
            processed_image_url = url_for('static', filename='processed/' + processed_filename)

            new_record = ClassificationResult(
                user_id=user.id,
                original_image=filename,
                processed_image=processed_filename,
                confidence_score=confidence_score,
                logo_status=logo_status
            )
            db.session.add(new_record)
            db.session.commit()

    history = ClassificationResult.query.filter_by(user_id=user.id)\
        .order_by(ClassificationResult.timestamp.desc()).all()

    return render_template(
        "user_page.html",
        user=user,
        classification_result=classification_result,
        uploaded_image_url=uploaded_image_url,
        processed_image_url=processed_image_url,
        confidence_score=confidence_score,
        logo_status=logo_status,
        color=color,
        history=history
    )


# History
@app.route('/history/<int:user_id>')
def history_page(user_id):
    user = User.query.get_or_404(user_id)
    history = ClassificationResult.query.filter_by(user_id=user.id).all()
    return render_template('history_page.html', user=user, history=history)


# ---------- ADMIN ROUTES ---------- #

# Admin Login
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form.get('admin_email')
        password = request.form.get('admin_password')

        if email == 'admin@example.com' and password == 'admin123':
            session['admin_logged_in'] = True
            session['admin_email'] = email
            return redirect(url_for('admin_dashboard'))

        flash("Invalid Admin Credentials", "error")
        return render_template('admin_login.html')

    return render_template('admin_login.html')


# Admin Dashboard
@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    search_query = request.args.get('search', '')
    page = request.args.get('page', 1, type=int)
    per_page = 5

    if search_query:
        users = User.query.filter(User.name.like(f"%{search_query}%")).paginate(page=page, per_page=per_page)
    else:
        users = User.query.paginate(page=page, per_page=per_page)

    return render_template('admin_dashboard.html', users=users)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash("You have logged out successfully!", "success")
    return redirect(url_for('register'))


# Admin Logout (FINAL)
@app.route('/admin/logout')
def admin_logout_route():
    session.pop('admin_logged_in', None)
    session.pop('admin_email', None)
    flash("Admin logged out successfully!", "admin")
    return redirect(url_for('admin_login'))


# Delete user
@app.route('/admin/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash("User deleted successfully!", "success")
    return redirect(url_for('admin_dashboard'))


# Static pages
@app.route('/how-it-works')
def how_it_works():
    return render_template('how_it_works.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')


if __name__ == '__main__':
    app.run(debug=True)
