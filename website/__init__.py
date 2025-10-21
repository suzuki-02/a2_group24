from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# (optional logging)
import logging
from logging.handlers import RotatingFileHandler
import os

db = SQLAlchemy()

# ---- error handlers ----
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
# ------------------------

# create a function that creates a web application
# a web server will run this web application
def create_app():
    app = Flask(__name__)
    app.debug = True  # NOTE: with debug=True, Flask's debugger will show for 500s
    app.secret_key = 'somesecretkey'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sitedata.sqlite'

    db.init_app(app)
    Bootstrap5(app)

<<<<<<< HEAD
   # initialise the login manager
   login_manager = LoginManager()
   login_manager.login_view = 'auth.login'
   login_manager.init_app(app)
   
   # create a user loader function takes userid and returns User
   from .models import User  # importing here to avoid circular references
   @login_manager.user_loader
   def load_user(user_id):
      return db.session.scalar(db.select(User).where(User.id == user_id))
=======
    # ---- login manager ----
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    from .models import User  # Event is used elsewhere; importing user is enough here

    @login_manager.user_loader
    def load_user(user_id):
        # Flask-Login passes str; cast if PK is int
        try:
            uid = int(user_id)
        except (TypeError, ValueError):
            return None
        return db.session.scalar(db.select(User).where(User.id == uid))
>>>>>>> Haris-first-branch

    # ---- blueprints ----
    # These match your repo: views.main_bp, auth.auth_bp, events.events_bp
    from . import views
    app.register_blueprint(views.main_bp)

    from . import auth
    app.register_blueprint(auth.auth_bp)

    from . import events
    app.register_blueprint(events.events_bp)

    # (optional) rotating file logger in production
    if not app.debug:
        os.makedirs('instance', exist_ok=True)
        handler = RotatingFileHandler('instance/app.log', maxBytes=1_000_000, backupCount=3)
        handler.setLevel(logging.INFO)
        handler.setFormatter(logging.Formatter('[%(asctime)s] %(levelname)s in %(module)s: %(message)s'))
        app.logger.addHandler(handler)

    # register 404/500 handlers
    register_error_handlers(app)

    return app