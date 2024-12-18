from datetime import datetime
import os
import sys
import pytest
import sqlalchemy as sqla
from app import create_app, db
from app.main.models import User, Instructor, Student, Course, CourseTaken, Position, CourseSection, Application
from config import Config
from werkzeug.security import generate_password_hash
from flask_login import logout_user

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Custom config for testing
class TestConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    SECRET_KEY = 'bad-bad-key'
    WTF_CSRF_ENABLED = False
    DEBUG = True
    TESTING = True

# Fixture to create the test client
@pytest.fixture(scope='module')
def test_client():
    flask_app = create_app(config_class=TestConfig)
    testing_client = flask_app.test_client()
    ctx = flask_app.app_context()
    ctx.push()
    yield testing_client
    logout_user()
    test_client.cookie_jar.clear()  # Clear the cookies (and session)
    ctx.pop()

# Fixture to initialize the database
@pytest.fixture
def init_database(test_client):
    # Create the database tables
    db.create_all()

    # Create a student and an instructor
    student = Student(
        username="student1", wpiID=1234,firstname="John",lastname="Doe",phoneNumber="1234567890",userType="Student",
        major1="CS",major2="Math",GPA=3.8,gradDate=datetime(2025, 5, 15)
    )
    student.set_password("password")

    instructor = Instructor(
        username="instructor1@wpi.edu",wpiID=5678,firstname="Jane",lastname="Smith",phoneNumber="0987654321",userType="Instructor"
    )
    instructor.set_password("password")

    db.session.add(student)
    db.session.add(instructor)
    db.session.commit()

    # Create a course
    course = Course(
        courseNum="CS101",
        courseTitle="Intro to CS",
        courseDescription="CS course description",
        courseDept="CS"
    )
    db.session.add(course)
    db.session.commit()

    # Create a course section
    course_section = CourseSection(
        courseid=course.id,
        instructorID=instructor.wpiID,
        term="2024A",
        courseSection="CS101-A"
    )
    db.session.add(course_section)
    db.session.commit()

    # Add a course taken by the student
    course_taken = CourseTaken(
        studentid=student.wpiID,
        courseid=course.id,
        grade="A",
        sa_status=True,
        term="2023A"
    )
    db.session.add(course_taken)

    # Create a position linked to the course section
    # position = Position(
    #     course_section_id=course_section.courseSectionID,
    #     minGPA=3.5,
    #     minGradeInCourse="B",
    #     previousSAExperience=False,
    #     previousSAExperienceInCourse=False,
    #     numSA=2
    # )
    # db.session.add(position)

    db.session.commit()

    yield db
    db.session.remove()
    db.drop_all()
    

# Test  student dashboard route
def test_student_dash(test_client, init_database):
    # Log in as the student
    student_user = User.query.filter_by(username="student1@wpi.edu").first()
    test_client.post('/student/logout')
    test_client.post('/login', data={"username": student_user.username, "password": "password"})  # Simulated login

    response = test_client.get('/studentDash')

    assert response.status_code == 200
    assert b'Welcome to Student Dashboard' in response.data
    assert b'Recommended Positions' in response.data
    assert b'Teaching Assistant for CS101' in response.data

# Test redirect if the user is an instructor
def test_redirect_if_instructor(test_client, init_database):
    instructor_user = User.query.filter_by(username="instructor1").first()
    test_client.post('/student/logout')
    test_client.post('/')
    test_client.post('/login', data={"username": instructor_user.username, "password": "password"})  # Simulated login

    response = test_client.get('/studentDash')
    
    # Check that the instructor is redirected
    assert response.status_code == 302
    assert b'Instructor Dashboard' in response.data  # Check for redirection to the instructor dashboard

# test hat student is redirected to login if no student record exists
def test_student_not_found(test_client, init_database):
    test_client.post('/student/logout')
    non_student_user = User(username="nonexistent", wpiID=9999, userType="Instructor")
    db.session.add(non_student_user)
    db.session.commit()

    test_client.post('/login', data={"username": non_student_user.username, "password": "password"})  # Simulated login

    response = test_client.get('/studentDash')

    # Check redirected to login with a flash message
    assert response.status_code == 302
    assert b'Current user is not recognized as a student.' in response.data


# Test editing the profile 
def test_edit_profile(test_client, init_database):
    test_client.post('/student/logout')
    # Log in as the student
    student_user = User.query.filter_by(username="student1").first()
    test_client.post('/login', data={"username": student_user.username, "password": "password"}) 

    # Send a POST request to the edit profile route
    response = test_client.post('/edit_profile', data={
        "firstname": "UpdatedFirstName",
        "lastname": "UpdatedLastName",
        "phoneNumber": "123-456-7890",
        "password": "newpassword"
    })
    
    # profile is updated and we get a success message
    assert response.status_code == 200
    assert b'Profile updated successfully!' in response.data

    updated_user = User.query.filter_by(wpiID=student_user.wpiID).first()
    assert updated_user.firstname == "UpdatedFirstName"
    assert updated_user.lastname == "UpdatedLastName"
    assert updated_user.phoneNumber == "123-456-7890"

# Testing lash message when a user is not a student
def test_flash_message_for_non_student(test_client, init_database):
    test_client.post('/student/logout')
    non_student_user = User(username="nonstudent", wpiID=99999, userType="Instructor")
    db.session.add(non_student_user)
    db.session.commit()

    test_client.post('/login', data={"username": non_student_user.username, "password": "password"})  # Simulated login

    response = test_client.get('/studentDash')
    
    # Check if the flash message is present
    assert b'Current user is not recognized as a student.' in response.data

def test_add_course_section_instructor(test_client, init_database):
    #testing login
    login_response = test_client.post(
    '/login', 
    data={'email': 'instructor1@wpi.edu', 'password': 'password', 'submit': True}, 
    follow_redirects=True
)
    assert login_response.status_code == 200


        # Post data to the route
    thiscourse = db.session.scalars(sqla.select(Course).where(Course.courseNum == "CS101")).first()

    response = test_client.post(
            '/instructor/create_course_section',
            data=dict(
                courseName = thiscourse.id,  
                courseTerm = '2025A',
                courseSection = '101'
            ),
            follow_redirects=True
        )
    
    assert response.status_code == 200
    assert b"Course section has been created!" in response.data

    newCourseSection = db.session.scalars(sqla.select(CourseSection).where(CourseSection.courseid == thiscourse.id).where(CourseSection.term == '2025A')).all()
    assert len(newCourseSection) == 1
    assert newCourseSection[0].term == '2025A'
    assert newCourseSection[0].courseSection == '101'

def test_create_sa_position(test_client, init_database):
    #testing login
    test_client.post('/student/logout')
    login_response = test_client.post(
    '/login', 

    data={'email': 'student1@wpi.edu', 'password': 'password', 'submit': True}, 
    follow_redirects=True
)
    assert login_response.status_code == 200


        # Post data to the route
    thisStudent = db.session.scalars(sqla.select(Student).where(Student.username== "student1@wpi.edu")).first()

    response = test_client.get('/' + str(thisStudent.id) + '/student-profile')
    assert response.status_code == 200
    assert b"Courses Taken" in response.data
    assert b"'s profile" in response.data


def test_get_student_profile_no_exist(test_client, init_database):
    #testing login
    test_client.post('/student/logout')
    login_response = test_client.post(
    '/login', 
    data={'email': 'student1@wpi.edu', 'password': 'password', 'submit': True}, 
    follow_redirects=True
)
    assert login_response.status_code == 200 


        # Post data to the route
    thisStudent = db.session.scalars(sqla.select(Student).where(Student.username== "student1@wpi.edu")).first()

    response = test_client.get('/' + "10000000" + '/student-profile') #fake id
    assert response.status_code == 302  # check for redirect (HTTP 302)

    # Follow the redirect to reach the page where the flash message will be shown
    response = test_client.get(response.location)  # response.location is where the redirect points
    assert b"The user doesn't exist" in response.data


def test_get_student_withdraw(test_client, init_database):
        #testing login
    test_client.cookie_jar.clear()  # This clears the session cookies
    test_client.post('/student/logout')
    login_response = test_client.post(
    '/login', 
    data={'email': 'student1@wpi.edu', 'password': 'password', 'submit': True}, 
    follow_redirects=True
    )
    assert login_response.status_code == 200


        # Post data to the route
    thisStudent = db.session.scalars(sqla.select(Student).where(Student.username== "student1@wpi.edu")).first()
    pos = db.session.scalars(sqla.select(Position)).first() #grab position defined above
    app = Application(positionID = pos.id, studentID = thisStudent.id)
    db.session.add(app)
    db.session.commit()
    
    response = test_client.get('/' + str(pos.id) + '/student_withdraw')
    assert response.status_code == 200
    assert b"Withdraw" in response.data #text on withdraw botton



def test_reject_student_instructor(test_client, init_database):
    test_client.post('/student/logout')
    test_client.post(
    '/login', 

    data={'email': 'instructor1@wpi.edu', 'password': 'password', 'submit': True}, 
    follow_redirects=True)

    assert login_response.status_code == 200

    #get course section
    newCourse = Course(
        courseNum="CS3133",
        courseTitle="Advanced AI",
        courseDescription="AI course description",
        courseDept="CS")
    db.session.add(newCourse)
    db.session.commit()


    thisCourseSection = db.session.scalars(sqla.select(CourseSection)).first()

    allCourseSections = db.session.scalars(sqla.select(CourseSection.instructorID)).all()

    response = test_client.post(
            '/instructor/create_sa_position',
            data=dict(
                courseSection = thisCourseSection,  
                mingpa = 3.8,
                mingrade = 'B',
                previousSAEXP = True,
                previousSAEXPInThisClass = False,
                numSA = 2
            ),
            follow_redirects=True
        )
    # print(f"Response data: {response.data}")
    assert response.status_code == 200

    # thisPosition = db.session.scalars(sqla.select(Position).where(Position.course_section_id == thisCourseSection.courseSectionID)).all()
    thisPosition = db.session.scalars(sqla.select(Position)).all()

    assert len(thisPosition) == 1

    assert thisPosition[0].minGPA == 3.8
    assert thisPosition[0].minGradeInCourse == 'B'
    assert thisPosition[0].previousSAExperience == True
    assert thisPosition[0].previousSAExperienceInCourse == False
    assert thisPosition[0].numSA == 2