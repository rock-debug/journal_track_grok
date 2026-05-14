import os
import logging
import secrets
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from sqlalchemy.orm import DeclarativeBase
from dotenv import load_dotenv
from prometheus_flask_exporter import PrometheusMetrics

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
app.secret_key = os.environ.get("SESSION_SECRET", secrets.token_hex(16))

# Configure database - Local SQLite
db_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'instance', 'research_assistant.db')
try:
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
except OSError:
    pass
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", f"sqlite:///{db_path}")

# Initialize Prometheus metrics exporter
metrics = PrometheusMetrics(app)
# Static information as metric
metrics.info('app_info', 'Journal Tracker Application info', version='1.0.0')

app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize database
db.init_app(app)

# Set up login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Import models and create tables
with app.app_context():
    try:
        from models import User, ResearchPaper, Patent, Note, Reminder
        db.create_all()
        logging.info("Database tables created successfully")
    except Exception as e:
        logging.warning(f"Could not create tables: {e}")

# Debug health check route (defined before importing routes to ensure it always works)
@app.route('/health')
def health_check():
    info = {
        "status": "ok",
        "groq_key_set": bool(os.environ.get("GROQ_API_KEY")),
        "session_secret_set": bool(os.environ.get("SESSION_SECRET")),
        "python_version": __import__('sys').version,
    }
    try:
        db.session.execute(db.text("SELECT 1"))
        info["database_connected"] = True
    except Exception as e:
        info["database_connected"] = False
        info["database_error"] = str(e)
    return jsonify(info)

# Import routes
try:
    from routes import *
    logging.info("Routes imported successfully")
except Exception as e:
    logging.error(f"Failed to import routes: {e}")

@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))
