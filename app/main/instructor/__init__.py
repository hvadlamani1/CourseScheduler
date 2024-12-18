from flask import Blueprint

instructor_blueprint = Blueprint('inst', __name__, template_folder='main/instructor/templates')

from app.main.instructor import instructor_routes