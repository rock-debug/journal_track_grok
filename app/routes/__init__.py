from app.routes.auth import auth_bp
from app.routes.dashboard import dashboard_bp
from app.routes.papers import papers_bp
from app.routes.patents import patents_bp
from app.routes.notes import notes_bp
from app.routes.reminders import reminders_bp
from app.routes.ai import ai_bp
from app.routes.search import search_bp
from app.routes.export import export_bp
from app.routes.admin import admin_bp

__all__ = [
    'auth_bp',
    'dashboard_bp',
    'papers_bp',
    'patents_bp',
    'notes_bp',
    'reminders_bp',
    'ai_bp',
    'search_bp',
    'export_bp',
    'admin_bp'
]
