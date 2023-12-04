from App.models import Course, Prerequisites
from App.controllers.prerequistes import (create_prereq, get_all_prerequisites)
from App.database import db
import json, csv

def createPrerequistes(prereqs, courseName):
    for prereq_code in prereqs:
        prereq_course = Course.query.filter_by(courseCode=prereq_code).first()
        
        if prereq_course:
            create_prereq(prereq_code,courseName) 

def create_course(code, name, rating, credits, prereqs, semester, year):
    already = get_course_by_courseCode(code)
    if already is None:
        course = Course(code, name, rating, credits, semester, year)

        if prereqs:
            createPrerequistes(prereqs, name)
            
        db.session.add(course)
        db.session.commit()
        return course
    else:
        return None

def createCoursesfromFile(file_path):
    try:
        with open(file_path, 'r') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                if not row['courseCode']:  # Skip empty lines
                    continue
                try:
                    courseCode = row["courseCode"]
                    courseName = row["courseName"]
                    credits = int(row["numCredits"])
                    rating = int(row["rating"])
                    prerequisites_codes = row["preReqs"].split(',')
                    semester = int(row["semesterOffered"])
                    year = int(row["yearOffered"])

                    course = create_course(courseCode, courseName, rating, credits, prerequisites_codes, semester, year)
                    print(f"Course Added: {courseName} ({courseCode})")

                except ValueError as e:
                    print(f"Error processing line: {row}. Error: {e}")

    except FileNotFoundError:
        print("File not found.")

    
def get_course_by_courseCode(code):
    return Course.query.filter_by(courseCode=code).first()

def courses_Sorted_byRating():
    courses =  Course.query.order_by(Course.rating.asc()).all()
    codes = []

    for c in courses:
        codes.append(c.courseCode)
    
    return codes

def courses_Sorted_byRating_Objects():
    return Course.query.order_by(Course.rating.asc()).all()
    

def get_prerequisites(code):
    course = get_course_by_courseCode(code)
    prereqs = get_all_prerequisites(course.courseName)
    return prereqs

def get_credits(code):
    course = get_course_by_courseCode(code)
    return course.credits if course else 0

def get_ratings(code):
    course = get_course_by_courseCode(code)
    return course.rating if course else 0



