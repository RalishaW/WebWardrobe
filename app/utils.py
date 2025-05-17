import os
from flask_login import login_user
import jwt
from datetime import datetime, timedelta, timezone
from flask import current_app, flash, redirect, url_for
from flask_mail import Message
from app import mail
from app import db
from rembg import remove 
from PIL import Image, UnidentifiedImageError

from werkzeug.security import check_password_hash
from app.models import User, ClothingItem, Outfit

UPLOAD_FOLDER = os.path.join('static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'jfif', 'webp'}
MAX_FILE_SIZE = 16 * 1024 * 1024


#-------------------------------
# Encode JWT token for reset password
#-------------------------------
def generate_reset_token(user_id, expires_sec=1800): # expires within 30 minutes
    now = datetime.now(timezone.utc)
    payload= {
        "user_id": user_id,
        'exp': now + timedelta(seconds=expires_sec),
        'iat': now,
    }
    key = current_app.config['SECRET_KEY']
    token = jwt.encode(payload, key, algorithm='HS256')
    return token

#---------------------------------------------------
# Decode and verify the JWT token for reset password
#----------------------------------------------------
def verify_reset_token(token):
    try:
        key = current_app.config['SECRET_KEY']
        payload = jwt.decode(token,key,algorithms=["HS256"])
        # Return user_id if verified
        return payload["user_id"]
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


# Function to make image transparent for Outfit generator
def make_image_transparent(input_path, output_path):
    try:
        input_image = Image.open(input_path)
        transparent = remove(input_image)

        output_path = os.path.splitext(output_path)[0] + '.png'
        transparent.save(output_path)

        return output_path

    except UnidentifiedImageError:
        print(f"[ERROR] Cannot identify image file: {input_path}")
        return input_path

    except Exception as e:
        print(f"[ERROR] Failed to process image {input_path}: {e}")
        return input_path
   


# Allowed file extensions function
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Size limit for image upload function
def size_limit(image):
    # Save the current position in the file, then reset to the beginning
    current_pos = image.tell()
    image.seek(0, os.SEEK_END)
    file_size = image.tell()
    image.seek(current_pos)  # Reset back to the original position
    
    # Check the file size
    if file_size > MAX_FILE_SIZE:
        return False
    return True

def try_to_login(email, password, remember):
    user = User.query.filter_by(email=email).first()

    if user and check_password_hash(user.password, password):
        login_user(user, remember)
        return True
    else:
        return False
    
# Notification module functions
def send_notification_welcome(email):
    # send welcome email
    msg = Message(
        "Welcome to Fashanise!",
        sender="noreply@fashanise.com",
        recipients=[email]
    )
    msg.body = "Start your own journey here."
    try:
        mail.send(msg)
    except Exception as e:
        current_app.logger.error(f"Failed to send email to {email}: {e}")

def send_notification_shared_outfit(current_email, receiver_email):
    msg = Message('An outfit has been shared to you', sender="noreply@fashanise.com", recipients=[receiver_email])
    msg.body = f"{current_email} sent you an outfit that you would want to see. Congratulations!"
    try:
        mail.send(msg)
    except Exception as e:
        current_app.logger.error(f"Failed to send email to {receiver_email}: {e}")

def send_notification_delete(email):
    msg = Message("Deleted account", sender="noreply@fashanise.com", recipients=[email])
    msg.body = f"We are sorry that you deleted your account. Hope to see you again soon!"
    try:
        mail.send(msg)
    except Exception as e:
        current_app.logger.error(f"Failed to send email to {email}: {e}")

# Cleanup function
# Cleanup outfits
def cleanup_outfits(user_id):
    outfits = Outfit.query.filter_by(user_id=user_id).all()
    for outfit in outfits:
        if outfit.preview_image:
            full_path = os.path.join(current_app.root_path, 'static', outfit.preview_image)
            if os.path.isfile(full_path):
                try:
                    os.remove(full_path)
                except Exception as e:
                    current_app.logger.warning(f"Could not delete outfit preview image: {full_path}. Reason: {e}")

def cleanup_clothing_items(user_id):
    clothing_items = ClothingItem.query.filter_by(user_id=user_id).all()
    for item in clothing_items:
        if item.image_path:
            full_path = os.path.join(current_app.root_path, 'static', item.image_path)
            if os.path.isfile(full_path):
                try:
                    os.remove(full_path)
                except Exception as e:
                    current_app.logger.warning(f"Could not delete clothing item image: {full_path}. Reason: {e}")
                    
def cleanup_profile_picture(user):
    default_pic = 'images/empty-profile-pic.png'
    if user.profile_picture and user.profile_picture != default_pic:
        full_path = os.path.join(current_app.root_path, 'static', user.profile_picture)
        if os.path.isfile(full_path):
            try:
                os.remove(full_path)
            except Exception as e:
                current_app.logger.warning(f"Could not delete profile picture: {full_path}. Reason: {e}")