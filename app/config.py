import os
import secrets

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or os.environ.get("SESSION_SECRET") or secrets.token_hex(16)
    
    # Database config
    db_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'instance', 'research_tracker.db')
    DEFAULT_DB_URI = f"sqlite:///{db_path}"
    
    # Convert postgres:// to postgresql:// if needed
    db_url = os.environ.get("DATABASE_URL", DEFAULT_DB_URI)
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
        
    SQLALCHEMY_DATABASE_URI = db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }
    
    # External APIs & AI Config
    GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
    GROQ_MODEL = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")
    CROSSREF_EMAIL = os.environ.get("CROSSREF_EMAIL", "researcher@example.com")
    
class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SECRET_KEY = "test-secret-key"
    WTF_CSRF_ENABLED = False

config_by_name = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig
}
