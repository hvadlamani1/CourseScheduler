from flask import Blueprint

main_blueprint = Blueprint('main', __name__, template_folder='main/templates')

from app.main import routes
