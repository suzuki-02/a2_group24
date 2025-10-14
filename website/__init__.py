<<<<<<< HEAD
# import flask - from 'package' import 'Class'
from flask import Flask, render_template, request
=======
from flask import Flask
>>>>>>> main
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# (optional logging)
import logging
from logging.handlers import RotatingFileHandler

db = SQLAlchemy()

<<<<<<< HEAD
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
=======
>>>>>>> main
def create_app():
   app = Flask(__name__)
   app.debug = True
   app.secret_key = 'somesecretkey'
   app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sitedata.sqlite'

   db.init_app(app)
   Bootstrap5(app)

   login_manager = LoginManager()
   login_manager.login_view = 'auth.login'
   login_manager.init_app(app)

   from .models import User, Event

   @login_manager.user_loader
   def load_user(user_id):
      return db.session.scalar(db.select(User).where(User.id == user_id))

   from . import views
   app.register_blueprint(views.main_bp)

   from . import auth
   app.register_blueprint(auth.auth_bp)

   from . import events
   app.register_blueprint(events.events_bp)

<<<<<<< HEAD
   # (optional) basic rotating file logger in production
   if not app.debug:
      handler = RotatingFileHandler('instance/app.log', maxBytes=1_000_000, backupCount=3)
      handler.setLevel(logging.INFO)
      handler.setFormatter(logging.Formatter('[%(asctime)s] %(levelname)s in %(module)s: %(message)s'))
      app.logger.addHandler(handler)

   # register 404/500 handlers
   register_error_handlers(app)

   return app
=======
   return app
>>>>>>> main
