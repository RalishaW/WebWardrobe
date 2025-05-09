import os
from app import app, db, models

#----------------------------------------------------------------------------------------------#
# Script to delete previous database and making new one for testing purpose on local machine   #
#----------------------------------------------------------------------------------------------#

# Remove existing db 
old_file = os.path.join('instance', 'fashanise.db')
if os.path.exists(old_file):
    os.remove('instance/fashanise.db')
    print("[INFO] Deleted old db file")


# Create new database
with app.app_context():
    db.create_all()
    print("[INFO] Fresh database tables created")



# # Remove existing migration folder
# old_migration = os.path.join('migrations')
# if os.path.exists(old_migration):
#     os.remove('migrations')
#     print("[INFO] Deleted old migrations folder")


# # Create new migration 


