#----------------------------------------------------------------------------------------------#
# Script to delete previous database and making new one for testing purpose on local machine   #
#----------------------------------------------------------------------------------------------#


import os
from app import create_app, db
from app.config import Config
from flask_migrate import upgrade

# Create app with default (development) config
app = create_app(Config)

# Path to the SQLite file in the instance folder
old_file = os.path.join(app.instance_path, 'fashanise.db')
if os.path.exists(old_file):
    os.remove(old_file)
    print("[INFO] Deleted old db file at %s" % old_file)

# Recreate database tables
with app.app_context():
    upgrade()
    print("[INFO] Fresh database tables created")



# # Remove existing migration folder
# old_migration = os.path.join('migrations')
# if os.path.exists(old_migration):
#     os.remove('migrations')
#     print("[INFO] Deleted old migrations folder")


# # Create new migration 


