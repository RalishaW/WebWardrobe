from app import app
from flask import render_template, redirect, url_for, request, flash, session
from flask_wtf import FlaskForm
from sqlalchemy.exc import IntegrityError
from app.models import db, User
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from app.models import User, ClothingItem, Outfit
from app.forms import LoginForm, SignupForm
import os
import time

# Introductory / Landing Page
@app.route("/")
def home():
    return render_template("home.html")

# Sign Up
@app.route("/signup", methods=["GET", "POST"])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        print('Form submitted and validated.')
        firstname = form.firstname.data
        lastname = form.lastname.data
        email = form.email.data
        password = generate_password_hash(form.password.data, method='pbkdf2:sha256')        
        new_user = User(
            firstname = firstname,
            lastname = lastname,
            email = email,
            password = password,
        )

        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Registration Successful! Please Login.', 'success')
            return redirect(url_for('login'))
        except IntegrityError:
            db.session.rollback()
            flash('Email already existed. Please use another email!', 'error')

    return render_template('signup.html', form=form)


# Log In
@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            session['logged_in'] = True
            session['email'] = user.email
            if form.remember.data:
                session.permanent = True
            flash('Login successful!', 'success')
            return redirect(url_for('wardrobe'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'error')

    return render_template("login.html", form=form)

# Core Pages
@app.route('/wardrobe')
def wardrobe():
    if not session.get('logged_in'):  # <-- FIXED here
        flash('You must be logged in to view your wardrobe.', 'error')
        return redirect(url_for('login'))
    
    user_email = session.get('email')
    user = User.query.filter_by(email=user_email).first()

    if user:     
        items = ClothingItem.query.filter_by(email=user.email).all()
        print(f"User email in session: {session.get('email')}")
        return render_template('wardrobe.html', wardrobe_items=items)
    else:
        flash('User not found', 'error')
        return redirect(url_for('login'))

@app.route('/wardrobe/add', methods=["POST"])
def add_clothing_item():
    # Adding clothing item to database
    if not session.get('logged_in'):
        flash('Please log in first.', 'error')
        return redirect(url_for('login'))
    
    user_email = session.get('email')
    user = User.query.filter_by(email=user_email).first()

    if not user:
        flash('User not found', 'error')
        return redirect(url_for('login'))
    
    image = request.files.get('image')
    color = request.form.get('color')
    season = request.form.get('season')
    clothing_type = request.form.get('type')
    occasion = request.form.get('occasion')

    if image and image.filename:
        filename = secure_filename(f"{int(time.time())}")
        upload_path = os.path.join('app', 'static', 'images', 'clothing_items')
        image.save(upload_path)

        new_item = ClothingItem(
            filename=filename,
            color = color,
            season = season,
            clothing_type = clothing_type,
            occasion = occasion,
            email=user.email
        )

        db.session.add(new_item)
        db.session.commit()
        flash('Item uploaded successfully', 'success')
    else:
        flash('No image uploaded', 'error')
        return redirect(url_for('wardrobe'))

@app.route('/outfits')
def outfits():
    return render_template('outfit.html')

@app.route('/analysis')
def analysis():
    return render_template('analysis.html')

@app.route('/social')
def social():
    return render_template('social.html')

# @app.route('/wardrobe')
# def add_item():
#     form = ClothingItem()
#     if 'image' not in request.files:
#         return 'No image file part', 400
    
#     file = request.files['image']
#     if file.filename == '':
#         return 'No selected file', 400
    
#     if file:
#         filename = secure_filename(file.filename)
