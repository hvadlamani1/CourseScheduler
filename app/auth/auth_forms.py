from flask_wtf import FlaskForm
from wtforms import FieldList, FormField, SelectField, StringField, SubmitField, TextAreaField,PasswordField, FloatField, DateField, BooleanField
from wtforms_sqlalchemy.fields import QuerySelectMultipleField
from wtforms.validators import  Length, DataRequired, Email,EqualTo, ValidationError
from wtforms.widgets import ListWidget, CheckboxInput
import sqlalchemy as sqla
from app import db
from app.main.models import User, Instructor, Student, Course


class StudentRegistrationForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    wpi_id = StringField("WPI ID", validators=[DataRequired()])
    firstname = StringField("First Name", validators=[DataRequired()])
    lastname = StringField("Last Name", validators=[DataRequired()])
    phoneNum = StringField("Phone Number", validators=[DataRequired()])
    Major = StringField("First Major", validators=[DataRequired()])
    Major2 = StringField("Second Major")
    GPA = FloatField("Overall GPA", validators=[DataRequired()])
    gradDate = DateField("Graduation Date", validators=[DataRequired()])

    coursesTaken = QuerySelectMultipleField(
        "Courses Taken",
        query_factory=lambda: db.session.scalars(sqla.select(Course).order_by(Course.courseTitle)),
        get_label=lambda course: f"{course.courseNum} - {course.courseTitle}",
        widget=ListWidget(prefix_label=False),
        option_widget=CheckboxInput(),
    )

    password = PasswordField("Password", validators=[DataRequired()])
    password2 = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("Register!")


    def validate_username(self,username):
        query = sqla.select(Student).where(Student.username == username.data)
        student = db.session.scalars(query).first()
        if student is not None:
            raise ValidationError('This Username Already Exists')
    
    def validate_email(self,wpi_id):
        query = sqla.select(Student).where(Student.wpiID == wpi_id.data)
        student = db.session.scalars(query).first()
        if student is not None:
            raise ValidationError('This WPI ID Already Exists')


class InstructorRegistrationForm(FlaskForm):
    username = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Retype Password', validators=[DataRequired(), EqualTo('password')])
    firstname = StringField('First Name', validators=[DataRequired()])
    lastname = StringField('Last Name', validators=[DataRequired()])
    phonenum = StringField('Phone Number', validators=[DataRequired()])
    wpiID = StringField('WPI-ID', validators=[DataRequired()])
    submit = SubmitField('Register!')

    def validate_username(self,username):
        query = sqla.select(Instructor).where(Instructor.username == username.data)
        instructor = db.session.scalars(query).first()
        if instructor is not None:
            raise ValidationError('This email Already Exists')

class LoginForm(FlaskForm):
    email = StringField('WPI Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')
    submit2 = SubmitField('SSOLogin')