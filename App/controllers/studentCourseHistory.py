from App.models import StudentCourseHistory
from App.controllers import (get_student_by_id, get_course_by_courseCode)
from App.database import db

def addCoursetoHistory(studentid, code, score):
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
    return StudentCourseHistory.query.filter(StudentCourseHistory.studentID == id, StudentCourseHistory.score >= 50)

def getCompletedCourseCodes(id):
    completed = getCompletedCourses(id)
    codes = []
    
    for c in completed:
        codes.append(c.code)
    
    return codes

def updateScore(id, code, score):
    completed = StudentCourseHistory.query.filter_by(studentID=id, code=code).first()
    if completed:
        completed.score = score
        db.session.commit()
    else:
        print("Course not found")

def getStudentCourseHistory(id):
    return StudentCourseHistory.query.filter_by(studentID=id).all()

def getStudentCourseHistoryJSON(id):
    courses = StudentCourseHistory.query.filter_by(studentID=id).all()
    if not courses:
        return []
    courses_json = [course.get_json() for course in courses]
    return courses_json
