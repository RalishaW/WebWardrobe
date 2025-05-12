from app import app
from flask import render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, login_user, current_user, logout_user
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func
from app.models import db, User, ClothingItem, Outfit, SharedOutfit, OutfitItem
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from app.forms import LoginForm, SignupForm, RequestResetPasswordForm, ResetPasswordForm
from app.utils import allowed_file, size_limit, make_image_transparent
import os
from app.utils import make_image_transparent, generate_reset_token, verify_reset_token
from app import mail
from flask_mail import Message
import os
import random
from PIL import Image
from collections import Counter
from pathlib import Path

# Introductory / Landing Page
@app.route("/")
def home():
    if current_user.is_authenticated:
        return redirect(url_for('wardrobe'))
    return render_template("home.html")

@app.route("/intro")
def intro():
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

        upload_folder = os.path.join(app.root_path, 'static', 'clothing_items')
        os.makedirs(upload_folder, exist_ok=True)

        filepath = os.path.join(upload_folder, filename)

        image.save(filepath)

        # Validate image
        try:
            Image.open(filepath).verify()
        except Exception:
            os.remove(filepath)
            flash('Uploaded file is not a valid image.', 'error')
            return redirect(url_for('wardrobe'))

        
        new_filepath = make_image_transparent(filepath, filepath)

        # Get only the path relative to static/
        try:
            relative_path = str(Path(new_filepath).relative_to(Path(app.root_path) / 'static'))
        except ValueError:
            relative_path = "clothing_items/" + filename

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
    occasion = request.form.get('occasion')
    season = request.form.get('season')

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
        occasion=occasion,
        season=season,
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

@app.route("/outfits/share", methods=["POST"])
def share_outfit():
    outfit_id = request.form.get("outfit_id")
    username = request.form.get("username")
    
    receiver = User.query.filter_by(username=username).first()
    if not receiver:
        flash("No user with that username found.", "error")
        return redirect(url_for("outfits"))

    shared = SharedOutfit(
        outfit_id=outfit_id,
        sender_id=current_user.id,
        receiver_id=receiver.id
    )
    db.session.add(shared)
    db.session.commit()
    
    flash("Outfit shared successfully!", "success")
    return redirect(url_for("outfits"))


@app.route('/analysis')
@login_required
def analysis():
    user_id = current_user.id

    total_item_value = ClothingItem.query.filter_by(user_id=user_id).count()
    outfits_created_value = Outfit.query.filter_by(user_id=user_id).count()

    # Most used item in outfits combination
    most_used_data = (
        # Getting ClothingItem and the times that the item appeared
        db.session.query(ClothingItem, func.count().label('usage_count'))
        # Link the ClothingItem with the outfit they appeared in
        .join(OutfitItem, ClothingItem.id == OutfitItem.clothing_item_id)
        # Only choose the ClothingItem of the current user
        .filter(ClothingItem.user_id == user_id)
        # Sort the items by the number of appearances
        .order_by(func.count().desc())
        # Get the first result
        .first()
    )

    if most_used_data is not None and most_used_data[0] is not None:
        most_used_item, usage_count = most_used_data
        item_image_url = url_for('static', filename=most_used_item.image_path)
        item_name = most_used_item.item_name
        number_of_mixed_outfits = usage_count
    else:
        item_image_url = url_for('static', filename='images/logo.png')
        item_name = None
        number_of_mixed_outfits = 0

    return render_template('analysis.html', 
                           total_item_value = total_item_value,
                           outfits_created_value=outfits_created_value,
                           item_image_url=item_image_url,
                           item_name=item_name,
                           number_of_mixed_outfits=number_of_mixed_outfits
                           )


# Analysis graph 
@app.route('/analysis/data')
@login_required
def get_analysis_data():
    user_id = current_user.id

    items = ClothingItem.query.filter_by(user_id=user_id).all()

    category_counts = Counter(item.type for item in items if item.type)
    season_counts = Counter(item.season for item in items if item.season)
    color_counts = Counter(item.color for item in items if item.color)

    # Limit display for 6 most common categories
    most_common_categories = dict(category_counts.most_common(6))
    # Limit display for 6 most used color only
    most_common_colors = dict(color_counts.most_common(6))

    return jsonify({
        'category_counts': most_common_categories,
        'season_counts': dict(season_counts),
        'color_counts': most_common_colors
    })

@app.route('/social')
@login_required
def social():
    shared_entries = SharedOutfit.query.filter_by(receiver_id=current_user.id).all()
    return render_template('social.html', shared_entries=shared_entries)

@app.route('/social/delete/<int:shared_id>', methods=['POST'])
@login_required
def delete_shared_outfit(shared_id):
    shared = SharedOutfit.query.get_or_404(shared_id)

    # Make sure the current user is the receiver
    if shared.receiver_id != current_user.id:
        flash("Unauthorized action.", "error")
        return redirect(url_for('social'))

    db.session.delete(shared)
    db.session.commit()
    flash("Shared outfit removed.", "success")
    return redirect(url_for('social'))




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