from flask import Blueprint

passport_blue = Blueprint('passport', __name__, url_prefix='/passport')

from . import views