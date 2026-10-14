import os
import logging
from flask import Flask, jsonify, render_template
from app.config import config_by_name
from app.extensions import db, login_manager, migrate, metrics

logger = logging.getLogger(__name__)

def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
        
    app = Flask(__name__)
    config_cls = config_by_name.get(config_name, config_by_name['default'])
    app.config.from_object(config_cls)
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    
    # Initialize Prometheus metrics (if not testing)
    if not app.config.get('TESTING'):
        try:
            metrics.init_app(app)
            metrics.info('app_info', 'Journal Tracker Application info', version='1.0.0')
        except Exception as e:
            logger.warning(f"Metrics init skipped: {e}")
            
    # User loader for Flask-Login
    from app.models.user import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
        
    # Register blueprints
    from app.routes import (
        auth_bp, dashboard_bp, papers_bp, patents_bp,
        notes_bp, reminders_bp, ai_bp, search_bp, export_bp, admin_bp
    )
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(papers_bp)
    app.register_blueprint(patents_bp)
    app.register_blueprint(notes_bp)
    app.register_blueprint(reminders_bp)
    app.register_blueprint(ai_bp)
    app.register_blueprint(search_bp)
    app.register_blueprint(export_bp)
    app.register_blueprint(admin_bp)
    
    # Error Handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    @app.errorhandler(403)
    def forbidden(e):
        return render_template('403.html'), 403

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('500.html'), 500

    # Health Check Endpoint
    @app.route('/health')
    def health_check():
        db_connected = False
        db_error = None
        try:
            db.session.execute(db.text("SELECT 1"))
            db_connected = True
        except Exception as ex:
            db_error = str(ex)
            
        return jsonify({
            "status": "healthy" if db_connected else "degraded",
            "database_connected": db_connected,
            "database_error": db_error,
            "groq_api_configured": bool(app.config.get("GROQ_API_KEY")),
            "version": "1.0.0"
        }), 200

    # Create tables automatically for SQLite/Dev
    with app.app_context():
        try:
            db.create_all()
        except Exception as e:
            logger.warning(f"db.create_all() exception: {e}")
            
    return app
