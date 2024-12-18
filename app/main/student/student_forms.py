from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import SubmitField, StringField, FloatField, PasswordField
from wtforms.validators import DataRequired, ValidationError, EqualTo
import sqlalchemy as sqla
from app import db
from app.main.models import Student, User

class EmptyApplyForm(FlaskForm):
    submit = SubmitField("Apply")

class EditForm(FlaskForm):
    firstname = StringField('First name', validators=[DataRequired()])
    lastname = StringField('Last name', validators=[DataRequired()])
    wpiEmail = StringField('WPI email', validators=[DataRequired()])
    phoneNum = StringField('Phone Number', validators=[DataRequired()])
    GPA = FloatField('GPA', validators=[DataRequired()])
    major1 = StringField('Major', validators=[DataRequired()])
    major2 = StringField('Second Major(Optional)')
    password = PasswordField('Password',validators=[DataRequired()])
    password2 = PasswordField('Password',validators=[DataRequired(),EqualTo('password')])
    submit = SubmitField('Post')
        
    def validate_wpiEmail(self, wpiEmail):
        query = sqla.select(User).where(User.username == wpiEmail.data)
        user = db.session.scalars(query).first()
        if user is not None:
            if user.id != current_user.id:
                raise ValidationError('The email is already exist')
            
class EmptyEditForm(FlaskForm):
    submit = SubmitField("Edit Profile")
