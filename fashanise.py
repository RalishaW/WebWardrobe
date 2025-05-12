from dotenv import load_dotenv
load_dotenv()

from app import create_app, Config
app = create_app(Config)