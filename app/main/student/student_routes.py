from app import db

from flask import render_template, flash, redirect, url_for, request, jsonify
from flask_login import login_user, login_required, current_user

from app.main.student import student_blueprint as bp_stud
from app.main.models import Course, CourseSection, Application, Student, Position, CourseTaken
from app.main.student.student_forms import EmptyApplyForm, EditForm, EmptyEditForm
import sqlalchemy as sqla
@bp_stud.route('/studentDash', methods=['GET', 'POST'])
@login_required
def studentDash():
    if current_user.userType == 'Instructor':
        return redirect(url_for('inst.instructorDash'))
    curr_student = db.session.get(Student, current_user.id)

    if not curr_student:
        flash("Current user is not recognized as a student.", "danger")
        return redirect(url_for('auth.login'))

    courses_taken = db.session.scalars(
        sqla.select(CourseTaken).where(CourseTaken.studentid == curr_student.id)
    ).all()
    student_courses = {ct.courseid: ct for ct in courses_taken}
    all_positions = db.session.scalars(sqla.select(Position)).all()

    #ranking algorithm
    def calculate_rank(position, course_taken):
        rank = 0

        #if SA experience in the same course
        if course_taken.sa_status and position.courseSection.courseid == course_taken.courseid:
            rank += 4
        
        #sa experience in general
        elif course_taken.sa_status:
            rank += 3
        
        #high grades
        if course_taken.grade == 'A':
            rank += 2
        elif course_taken.grade == 'B':
            rank+= 1

        return rank
    
    recommended_positions = []
    for position in all_positions:
        course_id = position.courseSection.courseid
        if course_id in student_courses:
            course_taken = student_courses[course_id]
            rank = calculate_rank(position, course_taken)

            if rank > 0:
                recommended_positions.append((position, rank))

    #sort by rank in descending order
    recommended_positions.sort(key=lambda x: x[1], reverse=True)

    #get positions 
    recommended_positions = [pos[0] for pos in recommended_positions]

    #get student's applications
    all_applications = current_user.get_applications()
    
    return render_template(
        "studentDash.html",
        recommended_positions=recommended_positions,
        all_positions=all_positions,
        all_applications = all_applications
    )


@bp_stud.route('/<position_id>/student_apply', methods=['GET', 'POST'])
@login_required
def student_apply(position_id):
     submit = EmptyApplyForm()
     edit = EmptyEditForm()
     pos = db.session.scalars(sqla.select(Position).where(Position.id == position_id)).first()
     app = db.session.scalars(sqla.select(Application).where(Application.studentID == current_user.id, Application.positionID == position_id)).first()
     if submit.validate_on_submit():
          #assume a studnent can apply even if they don't meet the minimum requirements
          #assume can't apply to full application
          if current_user.check_assignedToPosition():
              flash("You are already assigned to a position, you cannot apply to another.")
          elif pos is None:
               flash("The position you tried to apply for doesn't exist, application failed")
          elif app is not None and app.status == "withdrawn":
               app.status = "pending"
               db.session.add(app)
               db.session.commit()
               flash("Successfully Reapplied")
               return redirect(url_for('stud.studentDash'))
          elif app is not None:
              flash("You have already applied to the course")
              return redirect(url_for('stud.studentDash'))
          elif pos.isAssignedPositionsMax():
               flash("The position you tried to apply for is full, application failed")
          else:
               app = Application(positionID = position_id, studentID = current_user.id)      #note status is pending by default 
               db.session.add(app)
               db.session.commit()
               flash("Successfully Applied")
               return redirect(url_for('stud.studentDash'))
     return render_template("application.html", form = submit, position = pos, eform = edit)


@bp_stud.route('/<position_id>/student_withdraw', methods=['GET' ,'POST'])
@login_required
def student_withdraw(position_id):
    app = db.session.scalars(sqla.select(Application).where(Application.positionID == position_id).where(Application.studentID == current_user.id)).first()
    if app is None:
        print("app is none")
        print("position.id was {}".format(position_id))
        print("student.id was {}".format(current_user.id))
    app.status = "withdrawn"
    db.session.add(app)
    db.session.commit()
    app = db.session.scalars(sqla.select(Application).where(Application.positionID == position_id).where(Application.studentID == current_user.id)).first()

    data = {'position_id': app.positionID,
            'student_id': app.studentID,
            'status': app.status}
    return jsonify(data)




@bp_stud.route('/<student_id>/student-profile', methods=['GET'])
@login_required
def student_profile(student_id):
    student = db.session.get(Student, student_id)

    if student == None:
        flash("The user doesn't exist")
        return redirect(url_for('auth.login'))

    return render_template("studentProfile.html", student = student)

@bp_stud.route('/student/editprofile/<course_applying>',methods=['GET','POST'])
@login_required
def edit_profile(course_applying):
    eform = EditForm()
    courses_taken = db.session.scalars(sqla.select(CourseTaken).where(CourseTaken.studentid == current_user.id)).all()
    student_courses_id = {ct.courseid: ct for ct in courses_taken}

    student_courses = db.session.scalars(sqla.select(Course).where(Course.id.in_(student_courses_id))).all()

    courses_left = db.session.scalars(sqla.select(Course).where(Course.id.notin_(student_courses_id))).all()

    if request.method == 'POST':
        if eform.validate_on_submit():
            current_user.firstname = eform.firstname.data
            current_user.lastname = eform.lastname.data
            current_user.username = eform.wpiEmail.data
            current_user.phoneNumber = eform.phoneNum.data
            current_user.GPA = eform.GPA.data
            current_user.major1 = eform.major1.data
            current_user.major2 = eform.major2.data
            current_user.set_password(eform.password.data)

            db.session.add(current_user)
            db.session.commit()

            

    #process editing courses
            for i, courseTaken in enumerate(courses_taken):
                sa_status = request.form.get(f"sa_status_{i + 1}", "off") == "on"  # Retrieve the checkbox value
                grade = request.form.get(f"grade_{i + 1}", "N/A")  # Retrieve the grade value
                term = request.form.get(f"term_{i + 1}")
                delete_course = request.form.get(f"delete_course_{i+1}")
                
                

                if not term:  # Check for None or empty string
                    term = None

                
                if(delete_course is None):
                    continue

                thisCourse = db.session.scalars(sqla.select(CourseTaken).where(CourseTaken.studentid == current_user.id).where(CourseTaken.courseid == course.id)).first()
                
                if thisCourse:
                    db.session.delete(thisCourse)
                    db.session.commit()
                
                

                if(sa_status or grade != "N/A" or term):
                    addCourse = CourseTaken(
                            studentid=current_user.id,
                            courseid=courseTaken.courseid,
                            grade=grade,
                            sa_status=sa_status,
                            term = term
                        )
                    db.session.add(addCourse)
                    
                    db.session.commit()
    
    # Process adding courses
            for i, course in enumerate(courses_left):
                sa_status = request.form.get(f"sa_status_add{i + 1}", "off") == "on"  # Retrieve the checkbox value
                grade = request.form.get(f"grade_add{i + 1}", "N/A")  # Retrieve the grade value
                term = request.form.get(f"term_add{i + 1}")

                if not term:  # Check for None or empty string
                    term = None

                if(sa_status == False and grade == "N/A" and term is None):
                    continue

                new_course_taken = CourseTaken(
                    studentid=current_user.id,
                    courseid=course.id,
                    grade=grade,
                    sa_status=sa_status,
                    term = term
                )
                db.session.add(new_course_taken)
                db.session.commit()
        
                db.session.commit()

            flash("Your changes have been saved")
            if course_applying == '-1':
                return redirect(url_for('stud.student_profile', student_id = current_user.wpiID))
            else:
                return redirect(url_for('stud.student_apply', position_id = course_applying))
        

    elif request.method == 'GET':
        eform.firstname.data = current_user.firstname
        eform.lastname.data = current_user.lastname
        eform.wpiEmail.data = current_user.username
        eform.phoneNum.data = current_user.phoneNumber
        eform.GPA.data = current_user.GPA
        eform.major1.data = current_user.major1
        eform.major2.data = current_user.major2
    else:
        pass

    
    courses_taken = db.session.scalars(sqla.select(CourseTaken).where(CourseTaken.studentid == current_user.id)).all()
    student_courses_id = {ct.courseid: ct for ct in courses_taken}

    student_courses = db.session.scalars(sqla.select(Course).where(Course.id.in_(student_courses_id))).all()

    courses_left = db.session.scalars(sqla.select(Course).where(Course.id.notin_(student_courses_id))).all()
    return render_template('edit_studentProfile.html', title = 'Edit Profile', form = eform, 
                           student_courses = student_courses, courses_left = courses_left)

@bp_stud.route('/delete/course/<course_id>', methods=['POST'])
def delete_course(course_id):
    deleteCourse = db.session.get(CourseTaken, (current_user.id,course_id ))
    if not delete_course:
        print("Not found")
        return jsonify({'status': 'error', 'message': 'Course not found'}), 404
    
    db.session.delete(deleteCourse)
    db.session.commit()

    return jsonify({'status': 'success', 'message': 'Course has been deleted'}), 200

@bp_stud.route('/student/courseinfo/<student_id>/<course_id>', methods=['GET'])
@login_required
def get_course_info(student_id, course_id):
    if student_id != current_user.id:
        return jsonify({"error": "Unauthorized access"}), 403
    
    course_taken = db.session.scalar(
        sqla.select(CourseTaken)
        .where(CourseTaken.studentid == student_id, CourseTaken.courseid == course_id)
    )

    if not course_taken:
        return jsonify({"error": "Course not found for the student"}), 404

    course_info = {
        "sa_status": course_taken.sa_status,
        "grade": course_taken.grade,
        "term": course_taken.term,
    }

    return jsonify(course_info), 200
    

