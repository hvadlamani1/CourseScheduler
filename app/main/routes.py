from flask import jsonify, render_template, flash, redirect, url_for
from app import db

from app.main import main_blueprint as bp_main
from app.main.models import User, Instructor

from app.auth.auth_forms import InstructorRegistrationForm



