import os

UPLOAD_FOLDER_CLOTHING_ITEMS = 'app/static/images/clothing_items'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
MAX_FILE_SIZE = 16 * 1024 * 1024

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