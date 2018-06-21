from flask import Blueprint

bp = Blueprint('main', __name__)

from metabolite_database.main import routes  # noqa
