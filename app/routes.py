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
from app.utils import allowed_file, size_limit, make_image_transparent
import os
import random
from PIL import Image





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
    wardrobe_items = ClothingItem.query.filter_by(user_id = user.id).all()
    return render_template('wardrobe.html', wardrobe_items=wardrobe_items)

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

@app.route("/outfits", methods=["GET"])
@login_required
def outfits():
    user_id = current_user.id
    user_outfits = Outfit.query.filter_by(user_id=user_id).all()
    return render_template("outfit.html", outfits=user_outfits)


@app.route('/preview_outfit', methods=['POST'])
@login_required
def preview_outfit():
    occasion = request.form.get('occasion')
    season = request.form.get('season')

    clothing_items = ClothingItem.query.filter_by(user_id=current_user.id).all()

    # Smart categorization
    base_tops = []
    middle_tops = []
    outer_tops = []
    bottoms = []
    shoes = []
    accessories = []

    for item in clothing_items:
        if (item.occasion.lower() == occasion.lower() or item.occasion.lower() == 'other') and \
           (item.season.lower() == season.lower() or item.season.lower() == 'all season'):
            
            type_lower = item.type.lower()

            if type_lower in ["t-shirt", "shirt", "top"]:
                base_tops.append(item)
            elif type_lower in ["hoodie", "sweater"]:
                middle_tops.append(item)
            elif type_lower in ["jacket", "coat"]:
                outer_tops.append(item)
            elif type_lower in ["pant", "jeans", "shorts", "skirt"]:
                bottoms.append(item)
            elif type_lower == "shoes":
                shoes.append(item)
            elif type_lower == "accessory":
                accessories.append(item)

    # Smart selection
    selected_items = []

    # Base Top (always)
    if base_tops:
        selected_items.append(random.choice(base_tops))

    # Middle Top (optional if not Summer)
    if season.lower() != "summer" and middle_tops:
        selected_items.append(random.choice(middle_tops))

    # Outer Top (optional if Winter)
    if season.lower() == "winter" and outer_tops:
        selected_items.append(random.choice(outer_tops))

    # Bottom (always)
    if bottoms:
        selected_items.append(random.choice(bottoms))

    # Shoes (always)
    if shoes:
        selected_items.append(random.choice(shoes))

    # Accessories (optional - 50% chance)
    if accessories and random.random() < 0.5:
        selected_items.append(random.choice(accessories))

    if not selected_items:
        flash('No matching items found!', 'error')
        return redirect(url_for('outfits'))

    # Generate outfit preview image
    images = []
    for item in selected_items:
        img_path = os.path.join(app.root_path, 'static', item.image_path)
        img = Image.open(img_path).convert('RGBA')

        # Resize to smaller thumbnail size for preview
        img = img.resize((150, int(img.height * 150 / img.width)))
        images.append(img)

    max_width = max(img.width for img in images)
    total_height = sum(img.height for img in images) + (len(images)-1) * 10  # spacing

    preview_img = Image.new('RGBA', (max_width, total_height), (255, 255, 255, 0))
    y_offset = 0
    for img in images:
        preview_img.paste(img, (0, y_offset))
        y_offset += img.height + 10

    preview_filename = f"preview_{current_user.id}.png"
    preview_path = os.path.join(app.root_path, 'static', 'outfits', preview_filename)
    preview_img.save(preview_path)

    return render_template('outfit.html', preview_image=f"outfits/{preview_filename}", preview_items=selected_items, outfits=Outfit.query.filter_by(user_id=current_user.id).all())


@app.route('/save_outfit', methods=['POST'])
@login_required
def save_outfit():
    outfit_name = request.form.get('outfit_name')
    privacy = request.form.get('privacy')

    if not outfit_name or not privacy:
        flash('Please enter name and privacy.', 'error')
        return redirect(url_for('outfits'))

    preview_filename = f"preview_{current_user.id}.png"
    preview_path = os.path.join(app.root_path, 'static', 'outfits', preview_filename)

    if not os.path.exists(preview_path):
        flash('No preview available to save.', 'error')
        return redirect(url_for('outfits'))

    # Save Outfit record
    new_outfit = Outfit(
        outfit_name=outfit_name,
        privacy=privacy,
        occasion='N/A',
        season='N/A',
        user_id=current_user.id
    )
    db.session.add(new_outfit)
    db.session.commit()

    # Save preview permanently
    final_filename = f"{new_outfit.id}_outfit.png"
    final_path = os.path.join(app.root_path, 'static', 'outfits', final_filename)

    os.rename(preview_path, final_path)

    new_outfit.preview_image = f"outfits/{final_filename}"
    db.session.commit()

    if os.path.exists(preview_path):
        os.remove(preview_path)

    flash("Outfit saved!", "success")
    return redirect(url_for('outfits'))

@app.route('/outfits/delete/<int:outfit_id>', methods=["POST"])
@login_required
def delete_outfit(outfit_id):
    outfit = Outfit.query.get_or_404(outfit_id)

    # Check if outfit belongs to user
    if outfit.user_id != current_user.id:
        flash("You are not authorized to delete this outfit.", "error")
        return redirect(url_for('outfits'))

    # Delete preview image
    if outfit.preview_image:
        file_path = os.path.join(app.root_path, 'static', outfit.preview_image)
        if os.path.exists(file_path):
            os.remove(file_path)

    # Delete outfit
    db.session.delete(outfit)
    db.session.commit()

    flash("Outfit deleted successfully.", "success")
    return redirect(url_for('outfits'))


@app.route('/analysis')
@login_required
def analysis():
    return render_template('analysis.html')

@app.route('/social')
@login_required
def social():
    return render_template('social.html')

