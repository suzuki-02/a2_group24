from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import logging
from logging.handlers import RotatingFileHandler
import os

# Initialize extensions
db = SQLAlchemy()


# ---- Error Handlers ----
def register_error_handlers(app):
    @app.errorhandler(404)
    def not_found(e):
        # lightweight log for missing routes
        app.logger.info("404 at %s", request.path)
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def server_error(e):
        # ensure any failed transaction is rolled back
        try:
            db.session.rollback()
        except Exception:
            pass
        # full stacktrace in logs
        app.logger.exception("500 error at %s", request.path)
        return render_template("errors/500.html"), 500


# ---- Application Factory ----
def create_app():
    app = Flask(__name__)
    app.debug = False  # Set to False in production
    app.secret_key = 'somesecretkey'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sitedata.sqlite'

    # Initialize extensions
    db.init_app(app)
    Bootstrap5(app)

    # ---- Login Manager ----
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    # Import here to avoid circular imports
    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.scalar(db.select(User).where(User.id == user_id))

    # ---- Register Blueprints ----
    from . import views
    app.register_blueprint(views.main_bp)

    from . import auth
    app.register_blueprint(auth.auth_bp)

    from . import events
    app.register_blueprint(events.events_bp)

    # ---- Logging (only in production) ----
    if not app.debug:
        os.makedirs('instance', exist_ok=True)
        handler = RotatingFileHandler('instance/app.log', maxBytes=1_000_000, backupCount=3)
        handler.setLevel(logging.INFO)
        handler.setFormatter(logging.Formatter('[%(asctime)s] %(levelname)s in %(module)s: %(message)s'))
        app.logger.addHandler(handler)

    # ---- Register Error Handlers ----
    register_error_handlers(app)

    return app
