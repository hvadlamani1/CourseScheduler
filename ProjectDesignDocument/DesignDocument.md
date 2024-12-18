# Project Design Document

## Team Function Junction Student SA Website
--------
Prepared by:

* `Hemanth Vadlamani`,`WPI`
* `Aditya Patel`,`WPI`
* `Pierce Lindsay`,`WPI`
* `Michael Lin`,`WPI`
---

**Course** : CS 3733 - Software Engineering 

**Instructor**: Sakire Arslan Ay

---

## Table of Contents
- [1. Introduction](#1-introduction)
- [2. Software Design](#2-software-design)
    - [2.1 Database Model](#21-model)
    - [2.2 Subsystems and Interfaces](#22-subsystems-and-interfaces)
    - [2.2.1 Overview](#221-overview)
    - [2.2.2 Interfaces](#222-interfaces)
    - [2.3 User Interface Design](#23-view-and-user-interface-design)
- [3. References](#3-references)

<a name="revision-history"> </a>

### Document Revision History

| Name | Date | Changes | Version |
| ------ | ------ | --------- | --------- |
|Revision 1 |2024-11-15 |Initial draft | 1.0        |
|Revision 2      |2024-11-22      |Final Draft         | 2.0        |


# 1. Introduction

This document outlines the database model, user interface design, and subsystem routes for the SA management application. It provides a detailed description of the project’s structure, including user flows and functionality for both students and instructors. The system streamlines the SA recruitment process, enabling students to find and apply for SA positions while allowing instructors to efficiently manage and assign them.

# 2. Software Design

## 2.1 Database Model

<b>User</b><br> 
The user table holds all basic information such as username, password, and contact information.<br>
<b>Attributes:</b><br>
Username: String (wpi email)<br>
Password: String<br>
FirstName: String<br>
LastName: String<br>
Address: String<br>
PhoneNum: String<br>
wpi_ID: int (primary key)<br>
Account_type: String (tells the program whether the user is a student or instructor)<br>
<b>Methods:</b><br>
setHashPassword(String password)<br>
CheckPassword(String password)<br><br>


<b>Student</b><br>
The student table inherits from the user table to get all basic info such as username, password, and contact information. The student table also holds the student's id, wpi_ID, GPA, major, graduation date. The role of this table is to hold information regarding a student.<br> 
<b>Attributes:</b><br>
wpi_ID: int (primary key, foreign key)<br>
Major: String<br>
Major2: String (optional second major)<br>
GPA: float<br>
Graduation date: date<br>
<b>Methods:</b><br>
applyTo(CourseSection) (method to easily apply to a course)<br> 
getCoursesTaken()<br> 
getSAdCourses()<br>
withdrawPosition() (method to withdraw an application)<br><br>

<b>Course</b><br>
The course table stores information on courses WPI offers including courseID, course number, title, and description. All the courses in the program together act as a catalog instructors can use to add courses.<br>
<b>Attributes:</b><br>
CourseID: int (primary key)<br>
CourseNum: string (in the form of major and number: CS2337)<br>
CourseTitle: string<br>
CourseDescription: string<br><br>

<b>CoursesTaken</b><br>
The coursesTaken table is a relationship table between student and courses that holds studentId, courseId, year, term courseTakenIDand grade. The role of this table is to track all the courses a student has taken and the courses they have SAd.<br>
<b>Attributes:</b><br>
studentID: int (foreign, primary key)<br>
courseID: int (foreign, primary key) <br>
Grade: char<br>
SAd: bool (whether the student has SAd the course before)


<b>Instructor</b><br>
The instructor table inherits from the user table to get all basic info such as username, password, and contract information. The instructor table also holds the instructor's id. The role of this table is to hold information regarding an instructor. <br>
<b>Attributes:</b><br>
wpi_id: int (primary key, foreign key)<br>
<b>Methods:</b><br>
createCourseSection(Course, term, year, sas)<br>
getCourses()<br>
getSas() (gets SAs related to an instructor through their course sections with positions with assigned applications)<br><br>


<b>CourseSection</b><br>
The courseSection table holds the courseSection’s id, course's id, number, term, instructorId, and number of SA's in the course. It also holds the recommended qualification to be an SA. The role of this table to hold information regarding a specific course.<br>
<b>Attributes:</b><br>
CourseID: int (foreign)<br>
InstructorID int: (foreign)<br>
courseSectionID(primary): int<br>
Term: String (in the form of A24 or B26)<br>
Section: int <br>

<b>Position</b><br>
The Position table handles SA positions created for a course section. For each course section, there can be a respectful Position table that holds the SA positions minimum qualifications and the number of max positions available for students to apply for.<br>
<b>Attributes:</b><br>
PositionID: int (primary)<br>
CourseSectionID: int (foreign)<br>
minGPA: float<br>
minGradeInCourse: String (A or B)<br>
previousSAEXP: String (instructor enters any info pertaining to SA experience requirements)<br>
numPositions: int (number of SA positions attached to this Position)<br>
<b>Methods:</b><br>
AssignStudentSAPosition() (assigns a student to an open SA position slot)<br>
isAssignedPositionsMax() (returns true if all the SA position slots in the table are filled with assigned students)<br>
RejectStudentSAPosition() (rejects a student from any open SA position slots) <br>

<b>Application</b><br>
The Application table is for handling the relationship between a student and a Position. Students interact with course sections by applying for SAships and the table holds their application status, studentID, and PositionID.<br>
<b>Attributes:</b><br>
Application Status: String (either widthdrawn, assigned, pending, or rejected)<br>
StudentID: int (foreign, primary)<br>
CourseSectionID: int (foreign, primary)<br><br>


<b>Database UML Diagram:</b>
  <kbd>
      <img src="images/databaseUML.png"  border="2" width=800 height=800>
  </kbd>

## 2.2 Subsystems and Interfaces

### 2.2.1 Overview

<b>Software Architecture UML Diagram:</b>
  <kbd>
      <img src="images/Architecture_UML.png"  border="2" width=800 height=400>
  </kbd>

### 2.2.2 Interfaces

#### 2.2.2.1 Auth Routes

|   | Methods           | URL Path   | Description  |
|:--|:------------------|:-----------|:-------------|
|1. | login             |/login  | Logs the user into the application allowing access to different routes based on account type             |
|2. |logout             | /logout    | Logs users out             |
|3. | register_student             | /register_student   | Registered student account. based on fields specific to a student like gpa, classes taken major, etc              |
|4. | register_instructor  | /register_instructor  |Registers instructor account              |

#### 2.2.2.2 Main Routes Student

|   | Methods           | URL Path   | Description  |
|:--|:------------------|:-----------|:-------------|
|1. |studentDash              | /student/student-dashboard | Display student dashboard        |
|2. |  student_profile    | /student/student-profile| Display student profile             |
|3. |  student_edit_profile   | /student/student-edit-profile|   Edit student profile  |
|4. |  student_apply  | /student/{position id}/student-apply | Applying to SA position             |
|5. | student_withdraw | /student/{application id}/withdraw  | Withdraw a pending application             |
|6. |  recommend_position |  /student/recommend          | display position that fit with student's information             |
|7. | viewPosition | /student/view-position | View all published SA position

#### 2.2.2.3 Main Routes Instructor

|   | Methods           | URL Path   | Description  |
|:--|:------------------|:-----------|:-------------|
|1. | instructorDash             |  /instructor/instructor-dashboard   | Display instructor dashboard   |
|2. |  instructor_profile  |  /instructor/instructor-profile  | Display instructor profile  |
|3. | instructor_edit_profile     |  /instructor/instructor-edit-profile |Edit the profile |
|4. | create_course_section   | /instructor/create-course-section   |  Create a course section    |
|5. |  instructor_assignStudent   | /instructor/{application id}/assign-student  | Assign a student as SA of the course             |
|6. | create_sa_position   | /instructor/create-sa-position  |  Assign the number of SA and the requirement for the SA            |
|7. | reject | /instructor/{application id}/reject | Reject student application|
|8. | edit_SAPosition| /instructor/{position id}/edit-position | Edit existing SA position for change requirement and number of SA |
|9. |manage_application | /instructor/{course id}/manage-application |View all application for a course and decide whether assign or reject student application |

#### 2.2.2.4 Error Routes

|   | Methods           | URL Path   | Description  |
|:--|:------------------|:-----------|:-------------|
|1. |  not_found_error   | /404error           | Handles 404 error for when an expected file can’t be found             |
|2. |  internal_error | /500error   | Handles error 500 for when an unexpected internal error occurs             |                |            |              |

### 2.3 User Interface Design 

<b>index.html</b>

Purpose: Landing page where users can log in or navigate to registration page

Associated User Stories:
"As a user, I want to log in to my account with my WPI email and password."
"As a user, I want to log in to my account with my WPI Azure SSO (Single Sign-On)..."

 <kbd>
      <img src="images/Index.html.png"  border="2" width=800 height=1000>
  </kbd>
<br>
<br>
<br>
<br>
<b>student_register1.html</b>

Purpose: Registration page for students to enter personal information, academics, and create login credentials.

Associated User Stories:
"As a student, I want to be able to create a student account and enter my profile information (username (WPI email), password, contact info (name, last name, WPI ID, phone), additional info (GPA, major, graduation date, previously SA’d courses)) so that I can have a personalized account for managing my SA applications."


 <kbd>
      <img src="images/register_student.html.png"  border="2" width=800 height=1000>
  </kbd>
<br>
<br>
<br>
<br>
<b>instructor_register.html</b>

Purpose: Registration page for instructors to create an account.

Associated User Stories:
"As an instructor, I want to be able to create an instructor account and enter my profile information (username (WPI email), password, contact info (name, last name, WPI ID, phone))."

 <kbd>
      <img src="images/register_instructor.html.png"  border="2" width=800 height=800>
  </kbd>
<br>
<br>
<br>
<br>
<b>student_dashboard.html</b>

Purpose: Dashboard for students to view and manage SA applications and account information.

Associated User Stories:
“As a student, I want to view open SA opportunities…”
“As a student, I want to view a recommended SA positions list…”
“As a student, I want to check the status of my SA applications…”
“As a student, I want to withdraw my pending SA application…”
“As a student, I want to apply to one or more open SA opportunities…”

 <kbd>
      <img src="images/student_dashboard.html.png"  border="2" width=800 height=1000>
  </kbd>
<br>
<br>
<br>
<br>
<b>instructor_dashboard.html</b>

Purpose: Dashboard for instructors to manage courses, create SA positions, and assign SAs.

Associated User Stories:
“As an instructor, I want to add new courses that I will teach.”
“As an instructor, I want to create SA positions for my courses.”
“As an instructor, I want to view all the students who have applied…”
“As an instructor, I want to view the qualifications of each student who applied…”

 <kbd>
      <img src="images/manageApplications.html.png"  border="2" width=800 height=1000>
  </kbd>
<br>
<br>
<br>
<br>
<b>edit_student_profile.html</b>

Purpose: Page for students to update their profile information.

Associated User Stories:
"As a student, I want to be able to create a student account and enter my profile information (username (WPI email), password, contact info (name, last name, WPI ID, phone), additional info (GPA, major, graduation date, previously SA’d courses)) so that I can have a personalized account for managing my SA applications."

<kbd>
      <img src="images/student_edit_profile.html.png"  border="2" width=800 height=800>
  </kbd>
<br>
<br>
<br>
<br>
<b>edit_instructor_profile.html</b>

Purpose: Page for instructors to update their profile information.

Associated User Stories:
"As an instructor, I want to be able to create an instructor account and enter my profile information (username (WPI email), password, contact info (name, last name, WPI ID, phone))."
Functionality: Allows instructors to update contact information such as name, WPI ID, and phone number.

<kbd>
      <img src="images/instructor_edit_profile.html.png"  border="2" width=800 height=800>
  </kbd>
<br>
<br>
<br>
<br>
<b>create_sa_position.html</b>

Purpose: Page for instructors to create SA positions for each course section.

Associated User Stories:
“As an instructor, I want to create SA positions for my courses.”

<kbd>
      <img src="images/createSAPosition.html.png"  border="2" width=800 height=1000>
  </kbd>
<br>
<br>
<br>
<br>
<b>create.html</b>

Purpose: Page where instructors can create new courses.

Associated User Stories:
“As an instructor, I want to add new courses that I will teach.”
Functionality: Provides form fields for instructors to select course details such as title, course number, term, and section. Allows submission to add the course to the instructor’s dashboard.

<kbd>
      <img src="images/create_course_section.html.png"  border="2" width=800 height=1000>
  </kbd>
<br>
<br>
<br>
<br>
<b>edit_SAPosition.html</b>

Purpose: Page where instructors can edit SA Positions.

Associated User Stories:
“As an instructor, I want edit an SA Position"

<kbd>
      <img src="images/edit_SAPositon.html.png"  border="2" width=800 height=1000>
  </kbd>
<br>
<br>
<br>
<br>
<b>apply.html</b>

Purpose: An overlapping section where students can apply to SA Positions.

Associated User Stories:
“As a student, I want to apply to one or more open SA opportunities by specifying a year and term I want to SA and my previous experience with the course(grade achieved and when I took the course)."

<kbd>
      <img src="images/apply.html.png"  border="2" width=800 height=1000>
  </kbd>
<br>
<br>
<br>
<br>


# 3. References
