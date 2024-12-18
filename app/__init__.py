from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
from flask_login import LoginManager
from flask_moment import Moment
from flask_session import Session
import identity.web

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
moment = Moment()
app_session = Session()


def create_app(config_class = Config):
    app = Flask(__name__)
    app.config.from_object(config_class)  
    app.static_folder = config_class.STATIC_FOLDER
    app.template_folder = config_class.TEMPLATE_FOLDER_MAIN

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    moment.init_app(app)
    app_session.init_app(app)

    sso_auth = identity.web.Auth(
    session=session,
    authority=app.config["AUTHORITY"],
    client_id=app.config["CLIENT_ID"],
    client_credential=app.config["CLIENT_SECRET"],

)
    app.config['SSO_AUTH'] = sso_auth
    #register bps

    from app.main import main_blueprint as main
    main.template_folder = Config.TEMPLATE_FOLDER_MAIN
    app.register_blueprint(main)

    from app.main.student import student_blueprint as stud
    stud.template_folder = Config.TEMPLATE_FOLDER_STUD
    app.register_blueprint(stud)

    from app.main.instructor import instructor_blueprint as inst
    inst.template_folder = Config.TEMPLATE_FOLDER_INST
    app.register_blueprint(inst, url_prefix='/instructor')

    from app.auth import auth_blueprint as auth
    auth.template_folder = Config.TEMPLATE_FOLDER_AUTH
    app.register_blueprint(auth)

    from app.errors import errors_blueprint as errors
    errors.template_folder = Config.TEMPLATE_FOLDER_ERRORS
    app.register_blueprint(errors)

    return app


