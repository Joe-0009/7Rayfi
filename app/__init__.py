from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager
from flask_migrate import Migrate
import os

db = SQLAlchemy()
csrf = CSRFProtect()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'hjshjhdjah kjshkjdhjs'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static/profile_pics')
    
    db.init_app(app)
    csrf.init_app(app)
    migrate.init_app(app, db)

    from app.routes.auth import auth
    from app.routes.home import home
    from app.routes.profile import profile
    from app.routes.job import job
    from app.routes.worker import worker
    from app.routes.worker import worker
     
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(home, url_prefix='/')
    app.register_blueprint(profile, url_prefix='/profile')
    app.register_blueprint(job, url_prefix='/job')
    app.register_blueprint(worker, url_prefix='/worker')

    from .models import User, Note, Skill, Experience, Certification, Job, Review

    with app.app_context():
        db.create_all()

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app

def create_database(app):
    if not os.path.exists(os.path.join('website', 'database.db')):
        with app.app_context():
            db.create_all()
        print('Created Database!')
