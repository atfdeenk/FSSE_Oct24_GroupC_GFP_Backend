# # Load environment variables from .env file
from dotenv import load_dotenv

load_dotenv()

# Import necessary modules
from models import *
from config.settings import create_app
from instance.database import db


# Initialize the Flask application
app = create_app()
