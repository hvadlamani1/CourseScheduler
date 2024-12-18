from typing import Optional
from app import db, login
from flask_login import UserMixin
import sqlalchemy as sqla
import sqlalchemy.orm as sqlo
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone

@login.user_loader
def load_user(wpiID):
    return db.session.get(User, int(wpiID))


class User(db.Model, UserMixin):
    username: sqlo.Mapped[str] = sqlo.mapped_column(sqla.String(64), unique=True)
    password_hash: sqlo.Mapped[Optional[str]] = sqlo.mapped_column(sqla.String(256))
    firstname: sqlo.Mapped[str] = sqlo.mapped_column(sqla.String(200))
    lastname: sqlo.Mapped[str] = sqlo.mapped_column(sqla.String(200))
    phoneNumber: sqlo.Mapped[str] = sqlo.mapped_column(sqla.String(12))
    wpiID: sqlo.Mapped[int] = sqlo.mapped_column(primary_key = True)
    userType: sqlo.Mapped[str] = sqlo.mapped_column(sqla.String(20))

    __mapper_args__ = {
        'polymorphic_identity': 'User',
        'polymorphic_on': userType
    }

    def __repr__(self):
        return '<username: {} - wpi id: {}>'.format(self.username,self.wpiID)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Instructor(User):
    id: sqlo.Mapped[int] = sqlo.mapped_column(sqla.ForeignKey(User.wpiID), primary_key=True)
    courseSections : sqlo.WriteOnlyMapped['CourseSection'] = sqlo.relationship(back_populates = 'instructor')

    __mapper_args__ = {
        'polymorphic_identity': 'Instructor'
    }


class Student(User):
    id: sqlo.Mapped[int] = sqlo.mapped_column(sqla.ForeignKey(User.wpiID), primary_key=True)
    major1: sqlo.Mapped[str] = sqlo.mapped_column(sqla.String(50))
    major2: sqlo.Mapped[str] = sqlo.mapped_column(sqla.String(50))
    GPA: sqlo.Mapped[float] = sqlo.mapped_column(sqla.Float(24))
    gradDate: sqlo.Mapped[datetime] = sqlo.mapped_column()

    __mapper_args__ = {
        'polymorphic_identity': 'Student'
    }

    #relationships
    coursesTaken : sqlo.WriteOnlyMapped['CourseTaken'] = sqlo.relationship(back_populates = 'student')
    applications : sqlo.WriteOnlyMapped['Application'] = sqlo.relationship(back_populates = 'student')

    def get_coursesTaken(self):
        return db.session.scalars(sqla.select(CourseTaken).where(CourseTaken.studentid == self.id)).all()
    
    def get_hasCoursesTaken(self):
        if db.session.scalars(sqla.select(CourseTaken).where(CourseTaken.studentid == self.id)).all() is not None:
            return True
        else:
            return False
    
    def get_SAdCoursesTaken(self):
         courses = db.session.scalars(sqla.select(CourseTaken).where(CourseTaken.studentid == self.id)).all()
         sadCourses = []
         for c in courses:
             if c.sa_status:
                sadCourses.append(c)
         return sadCourses
    
    def check_studMeetsGPA(self, position):
        if self.GPA >= position.minGPA:
            return True
        else:
            return False
        
    def get_gradeInCourse(self, course): # returns grade and term grade achieved
        courses = self.get_coursesTaken()
        for c in courses:
            if c.course.id == course.id:
                return "{} in {}".format(c.grade, c.term)
        return "N/A" #default if they haven't taken the class

    def check_studMeetsCourseGrade(self, position):
        courses = self.get_coursesTaken()
        for c in courses:
            if c.course.id == position.courseSection.courseid:
                if c.grade <= position.minGradeInCourse: #less would mean closer to A which is higher
                    return True
        return False

    
    def check_studentTookCourse(self, course):
        courses = self.get_coursesTaken()
        for c in courses:
            if c.course.id == course.id:
                return True
        return False 


    def check_studentSACourse(self, course):
        courses = self.get_coursesTaken()
        for c in courses:
            if c.course.id == course.id:
                if c.sa_status:
                    return True
        return False

    def check_studentSABefore(self):
        courses = self.get_coursesTaken()
        for c in courses:
            if c.sa_status:
                return True
        return False         

    def check_studMeetsSAExperience(self, position):          
        if position.previousSAExperience is not True:
            return True
        elif self.check_studentSABefore() and position.previousSAExperience:
            return True
        else:
            return False
    
    def check_studMeetsCourseSAExperience(self, position):          
        if position.previousSAExperienceInCourse is not True:
            return True
        elif self.check_studentSACourse(position.courseSection.course) and position.previousSAExperienceInCourse:
            return True
        else:
            return False
        
    def check_applyedToPosition(self, position): # returns true if they have already applied to position
        app = db.session.scalars(sqla.select(Application).where(Application.studentID == self.id).where(Application.positionID == position.id)).first()
        if app is None:
            return False
        elif app.status == "withdrawn":
            return False
        else:
            return True
        
    def get_applications(self):
        apps = db.session.scalars(sqla.select(Application).where(Application.studentID == self.id)).all()
        return apps
    
    def check_assignedToPosition(self):
        app = db.session.scalars(sqla.select(Application).where(Application.studentID == self.id).where(Application.status == "assigned")).first()
        if app is None:
            return False
        else:
            return True
        
    def get_assignedPosition(self):
        app = db.session.scalars(sqla.select(Application).where(Application.studentID == self.id).where(Application.status == "assigned")).first()
        return app
        


    


class Course(db.Model):
    id: sqlo.Mapped[int] = sqlo.mapped_column(primary_key=True)
    courseNum: sqlo.Mapped[str] = sqlo.mapped_column(sqla.String(10))
    courseTitle: sqlo.Mapped[str] = sqlo.mapped_column(sqla.String(200))
    courseDescription: sqlo.Mapped[str] = sqlo.mapped_column(sqla.String(1000))
    #courseDept:
    courseDept : sqlo.Mapped[str] = sqlo.mapped_column(sqla.String(100))

    #relationships
    courseSections : sqlo.WriteOnlyMapped['CourseSection'] = sqlo.relationship(back_populates = 'course')
    coursesTaken : sqlo.WriteOnlyMapped['CourseTaken'] = sqlo.relationship(back_populates = 'course')

   


class CourseSection(db.Model):
    courseSectionID: sqlo.Mapped[int] = sqlo.mapped_column(primary_key=True)
    courseid: sqlo.Mapped[int] = sqlo.mapped_column(sqla.ForeignKey(Course.id))
    instructorID: sqlo.Mapped[int] = sqlo.mapped_column(sqla.ForeignKey(Instructor.id))
    term: sqlo.Mapped[str] = sqlo.mapped_column(sqla.String(10)) #in the form pf B24 or A27
    courseSection: sqlo.Mapped[str] = sqlo.mapped_column(sqla.String(10))

    # Relationships
    course: sqlo.Mapped[Course] = sqlo.relationship("Course", back_populates="courseSections")
    instructor: sqlo.Mapped[Instructor] = sqlo.relationship("Instructor", back_populates="courseSections")
    positions : sqlo.WriteOnlyMapped['Position'] = sqlo.relationship(back_populates = 'courseSection')

    def get_positions(self):
        return db.session.scalars(sqla.select(Position).where(Position.course_section_id == self.courseSectionID)).all()


class CourseTaken(db.Model):
    studentid: sqlo.Mapped[int] = sqlo.mapped_column(sqla.ForeignKey(Student.id), primary_key=True)
    courseid: sqlo.Mapped[int] = sqlo.mapped_column(sqla.ForeignKey(Course.id), primary_key = True)
    grade: sqlo.Mapped[str] = sqlo.mapped_column(sqla.String(10))
    sa_status: sqlo.Mapped[bool] = sqlo.mapped_column() 
    term : sqlo.Mapped[str] = sqlo.mapped_column(sqla.String(10))

    #relationships 
    course: sqlo.Mapped[Course] = sqlo.relationship("Course", back_populates="coursesTaken")
    student: sqlo.Mapped[Student] = sqlo.relationship("Student", back_populates="coursesTaken")

    


class Position(db.Model):
    id : sqlo.Mapped[int] = sqlo.mapped_column(primary_key=True)
    course_section_id : sqlo.Mapped[int] = sqlo.mapped_column(sqla.ForeignKey(CourseSection.courseSectionID))

    # qualification
    minGPA: sqlo.Mapped[float] = sqlo.mapped_column()
    minGradeInCourse: sqlo.Mapped[str] = sqlo.mapped_column(sqla.String(10))
    previousSAExperience : sqlo.Mapped[bool] = sqlo.mapped_column()
    previousSAExperienceInCourse : sqlo.Mapped[bool] = sqlo.mapped_column()
    numSA: sqlo.Mapped[int] = sqlo.mapped_column(default = 1)
    date : sqlo.Mapped[Optional[datetime]] = sqlo.mapped_column(default = lambda : datetime.now(timezone.utc))


    #relationships

    courseSection : sqlo.Mapped[CourseSection] = sqlo.relationship(back_populates = 'positions')
    applications : sqlo.WriteOnlyMapped['Application'] = sqlo.relationship(back_populates = 'position')

    #methods

    def isAssignedPositionsMax(self):
        apps = db.session.scalars(sqla.select(Application).where(Application.positionID == self.id)).all()
        i = 0
        for a in apps:
            if a.status == "assigned":
                i += 1
        if i >= self.numSA:
            return True
        else:
            return False
        
    def howManyAvailableSlots(self):
        apps = db.session.scalars(sqla.select(Application).where(Application.positionID == self.id)).all()
        i = 0
        for a in apps:
            if a.status == "assigned":
                i += 1
        if i >= self.numSA:
            return 0
        else:
            return self.numSA-i






class Application(db.Model):
    positionID : sqlo.Mapped[int] = sqlo.mapped_column(sqla.ForeignKey(Position.id), primary_key = True)
    studentID : sqlo.Mapped[int] = sqlo.mapped_column(sqla.ForeignKey(Student.id), primary_key = True)
    status : sqlo.Mapped[str] = sqlo.mapped_column(sqla.String(10), default = "pending") 

    #relationships

    position: sqlo.Mapped[Position] = sqlo.relationship("Position", back_populates="applications")
    student: sqlo.Mapped[Student] = sqlo.relationship("Student", back_populates="applications")

    def get_course(self):
        return self.position.courseSection.course
    
    def get_instructor(self):
        return self.position.courseSection.instructor




