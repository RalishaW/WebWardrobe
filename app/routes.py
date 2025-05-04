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
from app.utils import make_image_transparent

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

    user_id = current_user.id
    
    item_name = request.form['item_name']
    type_ = request.form['type']   
    color = request.form['color']
    season = request.form['season']
    occasion = request.form['occasion']

    image = request.files['image']

    if image and allowed_file(image.filename) and size_limit(image):
        filename = f"{user_id}_{secure_filename(image.filename)}"

        upload_folder = os.path.join(app.root_path, 'static', 'uploads')
        os.makedirs(upload_folder, exist_ok=True)

        filepath = os.path.join(upload_folder, filename)

        image.save(filepath)

        new_filepath = make_image_transparent(filepath, filepath)

        # Get only the path relative to static/
        relative_path = os.path.relpath(new_filepath, os.path.join(app.root_path, 'static'))

        new_item = ClothingItem(
            user_id=current_user.id,
            item_name=item_name,
            type=type_,
            color=color,
            season=season,
            occasion=occasion,
            image_path = relative_path
        )

        db.session.add(new_item)
        db.session.commit()

        flash('Item added successfully!', 'success')
    else:
        flash('Invalid file type or file size exceeds limit.', 'error')

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

