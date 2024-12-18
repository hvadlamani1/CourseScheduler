# Project Group Report - 2

## Team: `<FunctionJunction>`

List team members and their GitHub usernames

* `<Hemanth Vadlamani>`,`<hvadlamani2>`
* `<Aditya Patel>`,`<adityaapatel>`
* `<Pierce Lindsay>`,`<PierceLindsay>`
* `<Michael Lin>`,`<MikeLin0321>`

---
**Course** : CS 3733 - Software Engineering

**Instructor**: Sakire Arslan Ay

----
## 1. Iteration 2 - Summary

 * Include a summary of your `Iteration-2` accomplishments.
 * List the user stories completed in `Iteration-2`. Mention who worked on those user stories.

 Accomplishments in Iteration-2:

Implemented HTML and routing for student dashboard and application.html.
Added functionality to display application positions for students and application forms that display and compare the student's qualifications to the position's. 
Developed a modal for courses taken when students are registering.

Implemented the ability for students to apply to multiple open SA opportunities.
Created and integrated an ApplicationForm in student_forms.py to handle the submission of applications.
Set up a route /apply to manage SA position applications.

Built a model to associate students, SA positions, and applications in the database where applications acts as the relational table.


Developed a feature for instructors to view all students who have applied for SA positions.
Enhanced error handling using Materialize CSS for student and instructor registration and login processes.

Many UI and styling improvements, changed whole student dashboard  to make 

User Stories Completed in Iteration-2 and Contributors

"As a student, I want to apply to one or more open SA opportunities by specifying a year and term I want to SA and my previous experience with the course(grade achieved and when I took the course)"
Assigned to: Pierce Lindsay, Aditya Patel

"As an instructor, I want to view all the students who have applied for SA positions."
Assigned to: Michael Lin, Aditya Patel, Hemanth Vadlamani, Pierce Lindsay 

"As an instructor, I want to view the qualifications( i.e., GPA, grades earned in classes, and previous SA experience) of each student who applied for the position so that I can assign a student to the correct SA position"
Assigned to: Michael Lin, Hemanth Vadlamani

"As an instructor, I want to view all the students who have applied for SA positions"
Assigned to: Michael Lin, Hemanth Vadlamani

Error handling and UI improvements for forms and dashboards.
Assigned to: Aditya Patel, All Members (minor UI fixes)

“As a user, I want to be able to edit my profile”
Assigned to: Michael Lin, Hemanth Vadlamani



----
## 2. Iteration 2 - Sprint Retrospective

 * Include the outcome of your `Iteration-2 Scrum retrospective meetings`.
 * Mention the changes the team will be doing to improve itself as a result of the Scrum reflections.

 Successes:

The team met consistently and worked efficiently to complete tasks on time.
The team approved of changes made and collaborated to create a design we all approved of.
The feature for instructors to view student applications and for students to create applications and apply was successful.
The ability for instructors and students to edit their profiles was successfully implemented.

Issues:

Some delays occurred due to merging backend logic with frontend design, which caused minor integration issues.
Some complexity in setting up relationships in the database (student, SA position, and application).
Minor UI glitches when rendering the All SA Position list dynamically based on the student profile.
Many bugs required fixing throughout the iteration and could have been limited with more frequent testing.

----
## 3. Product Backlog refinement

 * Have you made any changes to your `product backlog` after `Iteration-2`? If so, please explain the changes here.

Added "edit_SAPosition" user story to allow instructors to modify existing SA positions.
Updated the backlog to prioritize integration testing and performance optimization.

----
## 4. Iteration 3 - Sprint Backlog

Include a draft of your `Iteration-3 sprint backlog`.
 * List the user stories you plan to complete in `Iteration-3`. Make sure to break down the larger user stories into smaller size stories. Mention the team member(s) who will work on each user story.
 * Make sure to update the "issues" on your GitHub repo accordingly.  




"As a student, I want to be able to withdraw my pending SA application so that I can manage my applications and focus on other opportunities if needed"
Assigned to: Pierce

"As a student, I want to check the status of my SA applications so that I can see the positions I’ve withdrawn, the ones that are still pending, and if I've been assigned to one"
Assigned to: Pierce

"As a student, I want to be able to view a recommended SA positions list, ranked by my previous SAships and grades in those classes so that I can apply to the most relevant positions."
Assigned to: Hemanth Vadlamani (lead), Aditya Patel

"As an instructor, I want to select a student applicant and successfully assign them to one of the open SA positions when there are still positions to the left and the student isn’t already assigned to another position."
Assigned to: Michael Lin (lead), Hemanth Vadlamani

"As a user, I want to log in to my account with my WPI Azure SSO( Single Sign On), so I only need to remember one set of credentials and have strong account security"
Assigned to: Aditya Patel

