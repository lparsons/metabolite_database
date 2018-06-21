from flask import Blueprint

bp = Blueprint('auth', __name__)

from metabolite_database.auth import routes  # noqa
