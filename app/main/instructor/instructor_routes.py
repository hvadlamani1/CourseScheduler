from app import db

from flask import render_template, flash, redirect, url_for, jsonify, request

from flask_login import login_user, current_user, logout_user,login_required

from app.main.instructor import instructor_blueprint as bp_inst
from app.main.instructor.instructor_forms import CreateCourseSectionForm, CreateSAPosition, EditForm
from app.main.models import Course, CourseSection, Instructor, User, Position, Application, Student
import sqlalchemy as sqla


@bp_inst.route('/instructorDash', methods=['GET'])
@bp_inst.route('/instructorDash/<int:display_sa_id>', methods=['GET'])
@login_required
def instructorDash(display_sa_id=None):
    #just in case a student is somehow here
    if current_user.userType == 'Student':
            return redirect(url_for('stud.studentDash'))

    course_sections = db.session.scalars(sqla.select(CourseSection).where(CourseSection.instructorID == current_user.id)).all()
    return render_template("instructorDash.html", courses=course_sections, display_sa_id=display_sa_id)


@bp_inst.route('/create_course_section', methods=['GET', 'POST'])
@login_required
def create_course_section():
    cform = CreateCourseSectionForm()

    if cform.validate_on_submit():
        curr_course = db.session.scalars(sqla.select(Course).where(Course.id == cform.courseName.data.id)).first()
        
        new_course_section = CourseSection(
            courseid = curr_course.id,
            #add current_user.id
            instructorID = current_user.id,
            term = cform.courseTerm.data,
            courseSection = cform.courseSection.data
        )

        db.session.add(new_course_section)
        db.session.commit()

        flash("Course section has been created!", "success")
        return redirect(url_for('inst.instructorDash'))
    
    return render_template("create_course_section.html", form=cform)



@bp_inst.route('/create_sa_position', methods=['GET', 'POST'])
@login_required
def create_sa_position():
    pform = CreateSAPosition()

    if pform.validate_on_submit():
        newSAPosition= Position(
            course_section_id = pform.courseSection.data.courseSectionID,
            minGPA = pform.mingpa.data,
            minGradeInCourse = pform.mingrade.data,
            previousSAExperience = pform.previousSAEXP.data,
            previousSAExperienceInCourse = pform.previousSAEXPInThisClass.data,
            numSA = pform.numSA.data)

        db.session.add(newSAPosition)
        db.session.commit()

        flash("SA position has been created!", "success")
        return redirect(url_for('inst.instructorDash'))

    return render_template("create_sa_position.html", form=pform)

@bp_inst.route('/instructor/<course_section_id>/student-data')
@login_required
def roster_data(course_section_id):
     courseSection = db.session.get(CourseSection, course_section_id)
     pos = courseSection.get_positions()
     
     if not pos:
         return jsonify({"error": "No positions available for this course section."}), 404
     
     #get first pos
     pos = courseSection.get_positions()[0]
     application = db.session.scalars(sqla.select(Application).where(Application.positionID == pos.id)).all()
     roster = []

     for app in application:
          student = db.session.get(Student, app.studentID)
          roster.append({
               'student_id':student.id,
               'student_username':student.username,
               'student_firstname':student.firstname,
               'student_lastname': student.lastname,
               'student_wpiID': student.wpiID,
               'student_phoneNum':student.phoneNumber,
               'student_major':student.major1,
               'student_gpa':student.GPA,
               'student_gradDate': student.gradDate,
               'student_status': app.status
          })

     return jsonify(roster)

@bp_inst.route('/<instructor_id>/instructor-profile', methods=['GET'])
@login_required
def instructor_profile(instructor_id):
    instructor = db.session.get(Instructor, instructor_id)

    if instructor == None:
        flash("The user doesn't exist")
        return redirect(url_for('auth.login'))

    return render_template("instructorProfile.html", instructor = instructor)

@bp_inst.route('/instructor/editprofile',methods=['GET','POST'])
@login_required
def edit_profile():
    eform = EditForm()
    if request.method == 'POST':
        if eform.validate_on_submit():
            current_user.firstname = eform.firstname.data
            current_user.lastname = eform.lastname.data
            current_user.username = eform.wpiEmail.data
            current_user.phoneNumber = eform.phoneNum.data
            current_user.set_password(eform.password.data)

            db.session.add(current_user)
            db.session.commit()
            flash("Your changes have been saved")
            return redirect(url_for('inst.instructor_profile', instructor_id = current_user.wpiID))
    elif request.method == 'GET':
        eform.firstname.data = current_user.firstname
        eform.lastname.data = current_user.lastname
        eform.wpiEmail.data = current_user.username
        eform.phoneNum.data = current_user.phoneNumber
    else:
        pass
    return render_template('editProfile.html', title = 'Edit Profile', form = eform)

@bp_inst.route('/instructor/<student_id>/<course_id>/assign-sa')
@login_required
def assign_sa(student_id, course_id):
    courseSection = db.session.get(CourseSection, course_id)
    if current_user.wpiID != courseSection.instructorID:
        flash("You can't assign SA for this course")
        return redirect(url_for('auth.login'))
    
    pos = courseSection.get_positions()[0]

    accepted = db.session.scalars(sqla.select(Application).where(Application.studentID == student_id, 
                                                                 Application.status == 'assigned')).first()
    
    if accepted != None:
        flash("The student have been already assigned as SA")
        return redirect(url_for('inst.instructorDash'))
    
    app = db.session.scalars(sqla.select(Application).where(Application.studentID == student_id, 
                                                            Application.positionID == pos.id,
                                                            Application.status == 'pending')).first()

    if app == None:
        flash("The application doesn't exit")
        return redirect(url_for('inst.instructorDash'))
    
    if pos.isAssignedPositionsMax():
        flash("there are enough SA for this course section")
        return redirect(url_for('inst.instructorDash'))
    
    new_app = app
    new_app.status = 'assigned'

    db.session.add(new_app)
    db.session.commit()
    flash("Successfully assign SA for {}".format(courseSection.course.courseTitle))

    return redirect(url_for('inst.instructorDash'))

@bp_inst.route('/instructor/<student_id>/<course_id>reject-application')
@login_required
def reject_application(student_id, course_id):
    courseSection = db.session.get(CourseSection, course_id)

    if current_user.wpiID != courseSection.instructorID:
        flash("You can't assign SA for this course")
        return redirect(url_for('auth.login'))
    
    pos = courseSection.get_positions()[0]

    application = db.session.scalars(sqla.select(Application).where(Application.studentID == student_id, 
                                                                    Application.positionID == pos.id)).first()
    
    if application == None:
        flash("The application does not exist")
        return redirect(url_for('inst.instructorDash'))
    elif application.status == 'assigned':
        flash("Can't reject a student who is already a SA for the course")
        return redirect(url_for('inst.instructorDash'))
    elif application.status == 'withdraw' or application.status == 'rejected':
        flash("The application have already been canceled")
        return redirect(url_for('inst.instructorDash'))
    else:
        new_app = application
        new_app.status = 'rejected'
        db.session.add(new_app)
        db.session.commit()
        flash("You have reject the application")

    return redirect(url_for('inst.instructorDash'))