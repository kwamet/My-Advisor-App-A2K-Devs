from App.database import db
from App.models import prerequisites
import json

class Course(db.Model):
    courseCode = db.Column(db.String(8), primary_key=True)
    courseName = db.Column(db.String(25))
    credits = db.Column(db.Integer)
    rating = db.Column(db.Integer)
    semester = db.Column(db.Integer, nullable=False)
    year = db.Column(db.Integer, nullable=False)

    offered = db.relationship('CoursesOfferedPerSem', backref ='courses', lazy=True)
    students = db.relationship('StudentCourseHistory', backref='courses', lazy=True)
    programs = db.relationship('ProgramCourses', backref='courses', lazy=True)
    prerequisites = db.relationship('Prerequisites', backref='courses', lazy = True)

    # planIds = db.relationship('CoursePlanCourses', backref='courses', lazy=True)
   
    
    def __init__(self, code, name, rating, credits, semester, year):
        self.courseCode = code
        self.courseName = name
        self.rating = rating
        self.credits = credits
        self.semester = semester
        self.year = year
    
    def get_json(self):
        return{
            'Course Code:': self.courseCode,
            'Course Name: ': self.courseName,
            'Course Rating: ': self.rating,
            'No. of Credits: ': self.credits,
            'Semester: ': self.semester,
            'Year: ': self.year
        }