from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import StringField, SubmitField, FloatField, IntegerField, PasswordField, BooleanField
from wtforms.validators import DataRequired, NumberRange, ValidationError, EqualTo
import sqlalchemy as sqla
from app import db
from app.main.models import User, Instructor, Student, Course, CourseSection, Position
from wtforms_sqlalchemy.fields import QuerySelectField
from wtforms.widgets import ListWidget, CheckboxInput

def courseQuery():
    return db.session.scalars(sqla.select(CourseSection).where(CourseSection.instructorID == current_user.id, CourseSection.positions == None)).all()

class CreateCourseSectionForm(FlaskForm):
    courseName = QuerySelectField('Course Name',
                             query_factory = lambda : db.session.scalars(sqla.select(Course)),
                             get_label =lambda theCourse : theCourse.courseTitle,
                             allow_blank=False)
    courseTerm = StringField('Course Term', validators=[DataRequired()])
    courseSection = StringField('Course Section', validators=[DataRequired()])
    submit = SubmitField('Create')

    #ensure the combination of course section and term are unique eventually

    
class CreateSAPosition(FlaskForm):
     courseSection = QuerySelectField('Course Section',
                                        query_factory= courseQuery, 
                                            get_label= lambda theCourseSection : theCourseSection.course.courseTitle + ' ' +theCourseSection.courseSection + ' ' + theCourseSection.term, 
                                            allow_blank=False)
     
     mingpa = FloatField('Minimum GPA', validators=[DataRequired()])
     mingrade = StringField('Minimum Grade Previously Achieved in this Course', validators=[DataRequired()])
     previousSAEXP = BooleanField("Previous SA Experience Required?")
     previousSAEXPInThisClass = BooleanField("Previous SA Experience in this Course Required?")
     numSA = IntegerField('Number of SA positions for Course Section', validators=[DataRequired(), NumberRange(min=1)])
     submit = SubmitField('Post Position')


class EditForm(FlaskForm):
    firstname = StringField('First name', validators=[DataRequired()])
    lastname = StringField('Last name', validators=[DataRequired()])
    wpiEmail = StringField('WPI email', validators=[DataRequired()])
    phoneNum = StringField('Phone Number', validators=[DataRequired()])
    password = PasswordField('Password',validators=[DataRequired()])
    password2 = PasswordField('Password',validators=[DataRequired(),EqualTo('password')])
    submit = SubmitField('Post')
        
    def validate_wpiEmail(self, wpiEmail):
        query = sqla.select(User).where(User.username == wpiEmail.data)
        user = db.session.scalars(query).first()
        if user is not None:
            if user.id != current_user.id:
                raise ValidationError('The email is already exist')

    


