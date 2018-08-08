from flask import Blueprint

admin_blue = Blueprint('admin', __name__, url_prefix='/admin')


from . import views
