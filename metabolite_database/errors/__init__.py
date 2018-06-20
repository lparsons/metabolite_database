from flask import Blueprint

bp = Blueprint('errors', __name__)

from metabolite_database.errors import handlers  # noqa
