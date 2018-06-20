from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from metabolite_database.errors import bp as errors_bp
app.register_blueprint(errors_bp)

from metabolite_database import routes  # noqa: E402,F401
from metabolite_database import models  # noqa: E402,F401


# @app.shell_context_processor
# def make_shell_context():
#     return {'db': db, 'User': User, 'Post': Post}
