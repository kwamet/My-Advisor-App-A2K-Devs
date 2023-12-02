from App.models import StudentCourseHistory
from App.controllers import (get_student_by_id, get_course_by_courseCode)
from App.database import db

def addCoursetoHistory(studentid, code):
    student  = get_student_by_id(studentid)
    if student:
        course = get_course_by_courseCode(code)
        if course:
            completed = StudentCourseHistory(studentid, code, score)
            db.session.add(completed)
            db.session.commit()
        else:
            print("Course doesn't exist")
    else:
        print("Student doesn't exist")
         

def getCompletedCourses(id):
    return StudentCourseHistory.query.filter(StudentCourseHistory.studentID == id, StudentCourseHistory.grade >= 50)

def getCompletedCourseCodes(id):
    completed = getCompletedCourses(id)
    codes = []
    
    for c in completed:
        codes.append(c.code)
    
    return codes

def updateGrade(id, code, grade):
    completed = StudentCourseHistory.query.filter_by(studentID=id, code=code).first()
    if completed:
        completed.grade = grade
        db.session.commit()
    else:
        print("Course not found")