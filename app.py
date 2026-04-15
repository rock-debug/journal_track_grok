import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from sqlalchemy.orm import DeclarativeBase
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Set up SQLAlchemy
class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create Flask app
app = Flask(__name__)

# Generate a random secret key if one isn't set
import secrets
app.secret_key = os.environ.get("SESSION_SECRET", secrets.token_hex(16))

# Configure database — use Supabase PostgreSQL (no SQLite fallback on serverless)
database_url = os.environ.get("DATABASE_URL")
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql+pg8000://", 1)
elif database_url and database_url.startswith("postgresql://"):
    database_url = database_url.replace("postgresql://", "postgresql+pg8000://", 1)

if database_url:
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
else:
    # Local fallback to SQLite
    db_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'instance', 'research_assistant.db')
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"

app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Configure session — use signed cookies (works on serverless, no filesystem needed)
app.config["SESSION_TYPE"] = "null"
app.config["SESSION_PERMANENT"] = False

# Initialize database
db.init_app(app)

# Set up login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Import models and create tables
with app.app_context():
    from models import User, ResearchPaper, Patent, Note, Reminder
    try:
        db.create_all()
    except Exception as e:
        logging.warning(f"Could not create tables (may already exist): {e}")

# Import routes
from routes import *

@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))
