from app import app, db
#from app.models import 
from config  import Config

import sqlalchemy as sqla
import sqlalchemy.orm as sqlo
from sqlalchemy import select
import os

from app.main.models import User, Instructor, Student, Course, CourseSection, Position, CourseTaken

    # id: sqlo.Mapped[int] = sqlo.mapped_column(primary_key=True)
    # courseNum: sqlo.Mapped[str] = sqlo.mapped_column(sqla.String(10))
    # courseName: sqlo.Mapped[str] = sqlo.mapped_column(sqla.String(200))
    # courseTitle: sqlo.Mapped[str] = sqlo.mapped_column(sqla.String(200))
    # courseDescription: sqlo.Mapped[str] = sqlo.mapped_column(sqla.String(1000))

#add courses to db
course1 = Course(
        courseNum="CS1101",
        courseTitle="Introduction to Programming",
        courseDescription="An overview of fundamental concepts in computer science, including programming, data structures, and algorithms."
    )

db.session.add(course1)

course2 = Course(
        courseNum="CS2223",
        courseTitle="Algorithms",
        courseDescription="Study of algorithm design and analysis, including sorting, searching, graph algorithms, and dynamic programming."
    )

db.session.add(course2)
db.session.commit()

#print courses
courses = db.session.scalars(sqla.select(Course)).all()

for c in courses:
    print(c.id)

#query INSTRUCTORS
instructors = db.session.scalars(sqla.select(Instructor)).all()

for i in instructors:
    print(i.id)

#QUERY FOR STUDENTS
students = db.session.scalars(sqla.select(Student)).all()

for s in students:
    print(s.id, s.firstname)

#QUERY CREATE COURSE SECTIONS
course_sections = db.session.scalars(sqla.select(CourseSection)).all()
for c in course_sections:
    print(c.courseSectionID)


for c in db.session.scalars(sqla.select(Position)).all():
    print(c.minGPA)

#query COURSE TAKEN
coursesTaken = db.session.scalars(sqla.select(CourseTaken)).all()

for c in coursesTaken:
    print(c.studentid)

#getting course name
allcourses = db.session.scalars(sqla.select(Course).where()).all()
for c in allcourses:
    print(f"{c.id} -- {c.courseTitle}")

