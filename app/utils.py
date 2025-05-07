import os
import jwt
from datetime import datetime, timedelta 
from flask import current_app

UPLOAD_FOLDER = os.path.join('static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'jfif', 'webp'}
MAX_FILE_SIZE = 16 * 1024 * 1024

from rembg import remove 
from PIL import Image

#-------------------------------
# Encode JWT token for reset password
#-------------------------------
def generate_reset_token(user_id, expires_sec=1800): # expires within 30 minutes
    payload= {
        "user_id": user_id,
        'exp': datetime.utcnow() + timedelta(seconds=expires_sec),
        'iat': datetime.utcnow(),
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
    input_image = Image.open(input_path)
    transparent = remove(input_image)

    output_path = os.path.splitext(output_path)[0] + '.png'
    transparent.save(output_path)

    return output_path   # <<== This return is important


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