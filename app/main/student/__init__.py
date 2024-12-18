from flask import Blueprint

student_blueprint = Blueprint('stud', __name__, template_folder='main/student/templates')

from app.main.student import student_routes