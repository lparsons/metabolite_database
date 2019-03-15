import logging
import os
from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from logging.handlers import SMTPHandler
from logging.handlers import RotatingFileHandler
from flask_bootstrap import Bootstrap
from sqlalchemy import MetaData
from flask_moment import Moment
# from flask_bootstrap import StaticCDN

naming_convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(column_0_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}
db = SQLAlchemy(metadata=MetaData(naming_convention=naming_convention))

migrate = Migrate()
bootstrap = Bootstrap()
moment = Moment()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    with app.app_context():
        if db.engine.url.drivername == 'sqlite':
            migrate.init_app(app, db, render_as_batch=True)
        else:
            migrate.init_app(app, db)
    bootstrap.init_app(app)
    # app.extensions['bootstrap']['cdns']['jquery'] = StaticCDN()
    moment.init_app(app)

    # Blueprint registration
    from metabolite_database.errors import bp as errors_bp  # noqa: E402,F401
    app.register_blueprint(errors_bp)
    from metabolite_database.main import bp as main_bp  # noqa: E402,F401
    app.register_blueprint(main_bp)
    from metabolite_database.auth import bp as auth_bp  # noqa: E402,F401
    app.register_blueprint(auth_bp)

    if not app.debug and not app.testing:
        if app.config['MAIL_SERVER']:
            auth = None
            if (app.config['MAIL_USERNAME']
                    or app.config['MAIL_PASSWORD']):
                auth = (app.config['MAIL_USERNAME'],
                        app.config['MAIL_PASSWORD'])
            secure = None
            if app.config['MAIL_USE_TLS']:
                secure = ()
            mail_handler = SMTPHandler(
                mailhost=(app.config['MAIL_SERVER'],
                          app.config['MAIL_PORT']),
                fromaddr='no-reply@' + app.config['MAIL_SERVER'],
                toaddrs=app.config['ADMINS'],
                subject='Microblog Failure',
                credentials=auth, secure=secure)
            mail_handler.setLevel(logging.ERROR)
            app.logger.addHandler(mail_handler)

        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/metabolite_database.log',
                                           maxBytes=10240,
                                           backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: '
            '%(message)s [in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('Metabolite Database startup')

    return app


from metabolite_database import models  # noqa: E402,F401


# @app.shell_context_processor
# def make_shell_context():
#     return {'db': db, 'User': User, 'Post': Post}
