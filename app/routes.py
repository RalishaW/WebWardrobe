from app import app
from flask import render_template, redirect, url_for, request, flash, session
from flask_wtf import FlaskForm
from flask_login import login_required, login_user, current_user, logout_user
from sqlalchemy.exc import IntegrityError
from app.models import db, User
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from app.models import User, ClothingItem, Outfit
from app.forms import LoginForm, SignupForm, ResetPasswordForm, ResetPasswordRequestForm
from app.utils import allowed_file, size_limit
import uuid
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
        username = form.username.data
        firstname = form.firstname.data
        lastname = form.lastname.data
        email = form.email.data
        password = generate_password_hash(form.password.data, method='pbkdf2:sha256')   

        existing_username = User.query.filter_by(username=username).first()
        existing_email = User.query.filter_by(email=email).first()

        if existing_email and existing_username:
            flash('Both email and username are already taken. Please use different ones.', 'error')
        elif existing_email:
            flash('Email already exists. Please use another email.', 'error')
        elif existing_username:
            flash('Username already taken. Please choose another one.', 'error')

        new_user = User(
            username = username,
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
            flash('Email or Username already existed. Please use another one!', 'error')

    return render_template('signup.html', form=form)


# Log In
@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user and check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            flash('Login successfully!', 'success')
            return redirect(url_for('wardrobe'))
        else:
            flash('Login Unsuccessful. Please check username and password.', 'error')
    
    return render_template("login.html", form=form)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('home'))

# Core Pages
@app.route('/wardrobe')
@login_required
def wardrobe():
    user = current_user
    items = ClothingItem.query.filter_by(user_id = user.id).all()
    return render_template('wardrobe.html', wardrobe_items=items)

@app.route('/wardrobe/add', methods=["POST"])
@login_required
def add_clothing_item():
    item_name = request.form['item_name']
    color = request.form['color']
    season = request.form['season']
    clothing_type = request.form['type']
    occasion = request.form['occasion']

    # Getting user id
    user_id = current_user.id

    image = request.files['image']
    if image and allowed_file(image.filename):
        # Check for size limit for upload file
        if not size_limit(image):
            flash('Image file is too large. Maximum size is 16MB.', 'error')
            return redirect(url_for('wardrobe'))
        
        filename = secure_filename(image.filename)
        filename = f"{uuid.uuid4()}"
        image_path = os.path.join(app.config['UPLOAD_CLOTHING_ITEM'], filename)
        image.save(image_path)

        new_item = ClothingItem(
            user_id = user_id,
            item_name = item_name,
            color = color,
            season = season,
            clothing_type = clothing_type, 
            occasion = occasion, 
            image_path = f"images/clothing_items/{filename}",
        )

        try:
            db.session.add(new_item)
            db.session.commit()
            flash(f'Clothing item {item_name} added successfully!', 'success')
            return redirect(url_for('wardrobe'))
        except IntegrityError:
            db.session.rollback()
            flash('Error adding clothing item. Please try again.', 'error')
    else:
        flash('Invalid image file. Please upload a jpeg, jpg or png image.', 'error')      

    return redirect(url_for('wardrobe'))


@app.route('/outfits')
@login_required
def outfits():
    return render_template('outfit.html')

@app.route('/analysis')
@login_required
def analysis():
    return render_template('analysis.html')

@app.route('/social')
@login_required
def social():
    return render_template('social.html')

