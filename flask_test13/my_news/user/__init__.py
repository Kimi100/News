from flask import Blueprint

user_blue = Blueprint('user', __name__, url_prefix='/user')

from . import views