from app import app
from flask import render_template, redirect, url_for, request, flash, session
from flask_login import login_required, login_user, current_user, logout_user
from sqlalchemy.exc import IntegrityError
from app.models import db, User, ClothingItem, Outfit
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from app.forms import LoginForm, SignupForm, RequestResetPasswordForm, ResetPasswordForm
from app.utils import allowed_file, size_limit
import os
from app.utils import make_image_transparent, generate_reset_token, verify_reset_token
from app import mail
from flask_mail import Message

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
            return render_template('signup.html', form=form)
        elif existing_email:
            flash('Email already exists. Please use another email.', 'error')
            return render_template('signup.html', form=form)
        elif existing_username:
            flash('Username already taken. Please choose another one.', 'error')
            return render_template('signup.html', form=form)
        
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
    wardrobe_items = ClothingItem.query.filter_by(user_id = user.id).all()
    return render_template('wardrobe.html', wardrobe_items=wardrobe_items)

# Add Clothing Item
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

# Delete Clothing Item
@app.route('/wardrobe/delete/<int:item_id>', methods=["POST"])
@login_required
def delete_clothing_item(item_id):
    item = ClothingItem.query.get_or_404(item_id)

    # Check if the item belongs to the logged-in user
    if item.user_id != current_user.id:
        flash("You are not authorized to delete this item.", "error")
        return redirect(url_for('wardrobe'))

    # Delete image from uploads
    file_path = os.path.join(app.root_path, 'static', item.image_path)
    if os.path.exists(file_path):
        os.remove(file_path)

    # Delete item from database
    db.session.delete(item)
    db.session.commit()

    flash("Item deleted successfully.", "success")
    return redirect(url_for('wardrobe'))

# Request Reset Password function
@app.route('/request_reset_password', methods=['GET','POST'])
def request_reset_password():
    request_form = RequestResetPasswordForm()

    if request_form.validate_on_submit():
        user = User.query.filter_by(email=request_form.email.data).first()
        # if user exists in the database, the link should be in their email
        if user:
            # Generate token
            token = generate_reset_token(user.id)

            # Reset_password url
            reset_password_url = url_for('reset_password', token=token, _external=True)

            # Send mail to the requested user
            msg = Message("Request Reset Password", sender='noreply@fashanise.com', recipients=[user.email])
            msg.body = f'Go to this link to reset your password:\n\n{reset_password_url}.'
            mail.send(msg)

        flash("If email is registed, an email will be sent to your inbox.", "info")
    return render_template('request_reset_password.html', form=request_form)

# Reset password using JWT Token
@app.route('/reset_password/token=<token>', methods=['GET', 'POST'])
def reset_password(token):
    form = ResetPasswordForm()

    # Verify the token
    user_id = verify_reset_token(token)
    if not user_id:
        flash('Invalid or expired token. Please try again.', 'error')
        # Return them back to request page
        return redirect(url_for('request_reset_password'))
    
    user = User.query.filter_by(id=user_id).first()

    if form.validate_on_submit():
        # hashed the password
        hashed_pwd = generate_password_hash(form.password.data)
        # Set the new password for the user
        user.password = hashed_pwd
        # Update password for user on database
        db.session.commit()
        flash('Successfully changed your password. Please login again.', 'success')
        return redirect(url_for('login'))
    
    if form.errors:
        print("Form errors", form.errors)

    return render_template('reset_password.html', form=form, token=token)


@app.route('/outfits', methods=['POST'])
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


# # Disable in deployment
# # Only for testing purpose
# # Test to send mail from fashanize@gmail.com to personal email, change accordingly
# # Run http://127.0.0.1:5000/test-email
# @app.route("/test-mail")
# def test_mail():
#     msg = Message(
#         subject="Hello Fashanize",
#         sender=app.config['MAIL_USERNAME'],
#         recipients=["personal_email@gmail.com"],
#         body="Test mail for Flask App"
#     )

#     mail.send(msg)
#     return "Success - send mail"