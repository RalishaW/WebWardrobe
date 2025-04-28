from app import app
from flask import render_template, redirect, url_for, request, flash, session
from flask_wtf import FlaskForm
from app.models import db, User
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
from app.models import ClothingItem

# Introductory / Landing Page
@app.route("/")
def home():
    return render_template("home.html")

# Sign Up
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm')

        if password != confirm_password:
            flash('Passwords do not match. Please try again.', 'error')
            return redirect(url_for('signup'))

        # Check if the email already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('An account with that email already exists. Please log in.', 'error')
            return redirect(url_for('signup'))

        # Hash the password
        # do later as this is not working rnhashed_password = generate_password_hash(password, method="pbkdf2:sha256")

        # Create a new user
        new_user = User(firstname=firstname, lastname=lastname, email=email, password=password)#hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template("signup.html")

# Log In
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if not user:
            flash('No account found with that email. Please sign up.', 'error')
            return redirect(url_for('login'))

        if user.password != password:
            flash('Incorrect password. Please try again.', 'error')
            return redirect(url_for('login'))

        # If login successful
        session['user_id'] = user.id
        session['user_email'] = user.email
        flash('Logged in successfully!', 'success')
        return redirect(url_for('wardrobe'))  # Redirect to wardrobe page after login

    return render_template("login.html")
    

# Core Pages
@app.route('/wardrobe')
def wardrobe():
    return render_template('wardrobe.html')

@app.route('/outfits')
def outfits():
    return render_template('outfit.html')

@app.route('/analysis')
def analysis():
    return render_template('analysis.html')

@app.route('/social')
def social():
    return render_template('social.html')

@app.route('/wardrobe')
def add_item():
    form = ClothingItem()
    if 'image' not in request.files:
        return 'No image file part', 400
    
    file = request.files['image']
    if file.filename == '':
        return 'No selected file', 400
    
    if file:
        filename = secure_filename(file.filename)
