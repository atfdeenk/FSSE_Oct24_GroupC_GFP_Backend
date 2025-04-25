from models import *
from config.settings import create_app
from config.config import LocalConfig
from instance.database import db


# Initialize the Flask application
app = create_app(LocalConfig)


