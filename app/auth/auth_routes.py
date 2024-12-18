from flask import render_template, flash, redirect, request, url_for, session, current_app
from flask_login import login_user, current_user, logout_user,login_required
from app import db
from app.auth import auth_blueprint as bp_auth 
from app.auth.auth_forms import InstructorRegistrationForm, StudentRegistrationForm, LoginForm
from app.main.models import Course, User, Instructor, Student, CourseTaken
import sqlalchemy as sqla
import identity.web


@bp_auth.route('/register_instructor', methods=['GET', 'POST'])
def register_instructor():
    iform = InstructorRegistrationForm()

    if iform.validate_on_submit():
        new_user = Instructor(username = iform.username.data,
                        firstname = iform.firstname.data,
                        lastname = iform.lastname.data,
                        phoneNumber = iform.phonenum.data,
                        id = iform.wpiID.data,
                        userType="Instructor"
                        )
        new_user.set_password(iform.password.data)
        db.session.add(new_user)
        db.session.commit()

        #creating new instructor
        # new_instructor = Instructor(id = new_user.id)
        # db.session.add(new_instructor)
        # db.session.commit()

        flash("New Instructor has been created!")
        return redirect(url_for('auth.login'))
    return render_template('/register_instructor.html', form=iform)

@bp_auth.route('/register_student', methods=['GET', 'POST'])
def register_student():
    sform = StudentRegistrationForm()

    all_courses = db.session.scalars(sqla.select(Course)).all()

    if sform.validate_on_submit():
        # Create the new student
        new_user = Student(
            username=sform.username.data,
            firstname=sform.firstname.data,
            lastname=sform.lastname.data,
            phoneNumber=sform.phoneNum.data,
            wpiID=sform.wpi_id.data,
            major1=sform.Major.data,
            major2=sform.Major2.data,
            GPA=sform.GPA.data,
            gradDate=sform.gradDate.data,
            userType='Student',
        )
        new_user.set_password(sform.password.data)
        db.session.add(new_user)
        db.session.commit()
        
        # Process courses dynamically
        for i, course in enumerate(all_courses):
            sa_status = request.form.get(f"sa_status_{i + 1}", "off") == "on"  # Retrieve the checkbox value
            grade = request.form.get(f"grade_{i + 1}", "N/A")  # Retrieve the grade value
            term = request.form.get(f"term_{i + 1}")

            if(sa_status == False and grade == "N/A"):
                continue

            new_course_taken = CourseTaken(
                studentid=new_user.id,
                courseid=course.id,
                grade=grade,
                sa_status=sa_status,
                term = term
            )
            db.session.add(new_course_taken)
            db.session.commit()
            print(f"Added CourseTaken: {new_course_taken}")
        
        db.session.commit()

        flash("New Student has been created!")
        return redirect(url_for('auth.login'))

    return render_template('/register_student.html', form=sform)

@bp_auth.route('/', methods=['GET', 'POST'])
@bp_auth.route('/login', methods=['GET', 'POST'])
def login():
    print("login called")
    if current_user.is_authenticated:
        print(current_user.username)
        print(current_user.id)
        print(current_user.userType)
    if current_user.is_authenticated:
        if current_user.userType == 'Student':
            print("stud called")
            return redirect(url_for('stud.studentDash'))
        elif current_user.userType == 'Instructor':
            print("inst called")
            return redirect(url_for('inst.instructorDash'))
    else:

        form = LoginForm()
        if form.validate_on_submit():
            email = form.email.data
            password = form.password.data
            user = User.query.filter_by(username=email).first()  
            if user and user.check_password(password):
                login_user(user)
                if user.userType == 'Student':
                    print("logged in student")
                    return redirect(url_for('stud.studentDash'))  # Redirect to student dashboard
                elif user.userType == 'Instructor':
                    print("logged in instructor")
                    return redirect(url_for('inst.instructorDash'))  # Redirect to instructor dashboard
                    
                

                else:
                    flash('Unknown user type.', 'danger')

            else:
                flash('Invalid email or password.', 'danger')
        return render_template('login.html', title="Login", form=form)
    
@bp_auth.route('/ssologin', methods=['GET', 'POST'])
def ssologin():
    sso_auth = current_app.config['SSO_AUTH']
    # Step 1: If not authenticated, trigger login
    if not sso_auth.get_user():
            auth_uri =sso_auth.log_in(
                scopes=current_app.config["SCOPE"],  
                redirect_uri=url_for("auth.auth_response", _external=True),
                prompt="select_account",  
            )
            return render_template("ssologin.html", auth_uri=auth_uri)

    # Step 2: Handle authentication response
    sso_user_info = sso_auth.get_user()  # User info after successful authentication
    email = sso_user_info.get("email")

    if email:
        user = User.query.filter_by(username=email).first()
        if user:
            login_user(user)
            if user.userType == 'Student':
                return redirect(url_for('stud.studentDash')) 
            elif user.userType == 'Instructor':
                return redirect(url_for('inst.instructorDash')) 
            else:
                flash('Unknown user type.', 'danger')
                return redirect(url_for('auth.login'))
        else:
            flash('No account found for this SSO user. Please contact support or register.', 'danger')
            return redirect(url_for('auth.login'))

    flash('Authentication failed. Please try again.', 'danger')
    return redirect(url_for('auth.login'))


@bp_auth.route('/getAToken', methods=['GET'])

def auth_response():
    sso_auth = current_app.config['SSO_AUTH']

    result = sso_auth.complete_log_in(request.args)

    if "error" in result:
        flash("SSO login failed! Error: " + str(result))
        return redirect(url_for('auth.login'))
    
    print(sso_auth.get_user())
    
    user_info = sso_auth.get_user()
    user = db.session.scalars(sqla.select(User).filter(User.username == user_info["preferred_username"])).first()

    if user is None:
        flash("User does not exist! Please register first!")
        return redirect(url_for('auth.register'))

    login_user(user, remember=False)
    session['ssologin'] = sso_auth.get_user()["preferred_username"]

    flash("SSO login successful! Username: {}".format(current_user.username), "success")

    if current_user.userType == 'Student':
        return redirect(url_for('stud.studentDash'))  # Redirect to student dashboard
    elif current_user.userType == 'Instructor':
        return redirect(url_for('inst.instructorDash'))  # Redirect to instructor dashboard
    else:
        return redirect(url_for('auth.login')) 

@bp_auth.route('/student/logout',methods=['GET'])
@login_required
def logout():
    logout_user() 

    # If logged in via SSO, log out from SSO as well
    if session.get('ssologin') is not None:
        sso_auth = current_app.config['SSO_AUTH']
        sso_auth.log_out(url_for("auth.login", _external=True))

    return redirect(url_for('auth.login'))


@bp_auth.route('/about')
def about_us():
    return render_template('about_us.html')
