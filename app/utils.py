import os

UPLOAD_FOLDER = os.path.join('static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'jfif', 'webp'}
MAX_FILE_SIZE = 16 * 1024 * 1024

from rembg import remove 
from PIL import Image

def make_image_transparent(input_path, output_path):
    input_image = Image.open(input_path)
    transparent = remove(input_image)

    output_path = os.path.splitext(output_path)[0] + '.png'
    transparent.save(output_path)

    return output_path   # <<== This return is important


# Allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Size limit for image upload
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