import os
import logging

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.utils import secure_filename


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'qlite:///xfishfarmer.db'  # Replace with your database URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False



# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Define base class for SQLAlchemy models
class Base(DeclarativeBase):
    pass

# Initialize SQLAlchemy
db = SQLAlchemy(model_class=Base)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")

# Configure database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///xfishfarmer.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Configure file uploads
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'svg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload size

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize database with app
db.init_app(app)

# Import routes (must be after app is created to avoid circular imports)
from routes import *

# Create database tables
with app.app_context():
    # Import models (must be after db is created to avoid circular imports)
    import models
    db.create_all()
    
    # Initialize company data if it doesn't exist
    from models import Company
    if not Company.query.first():
        default_company = Company(
            name="XFishFarmer Inc.",
            address="123 Fish Lane, Ocean City",
            phone="555-FISH-999",
            email="info@xfishfarmer.com"
        )
        db.session.add(default_company)
        db.session.commit()
