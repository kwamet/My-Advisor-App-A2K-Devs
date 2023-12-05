from App.database import db
import json

class CoursePlan(db.Model):
    planId=db.Column(db.Integer, primary_key=True)
    studentId=db.Column(db.Integer,  db.ForeignKey('student.id'), nullable=False)
    semester=db.Column(db.Integer, nullable=False)
    year=db.Column(db.Integer, nullable=False)
    student = db.relationship('Student', backref=db.backref('course_plans', uselist=True))
    courses_data = db.Column(db.Text)

    def __init__(self, studentid, semester, year):
        self.studentId = studentid
        self.courses_data = json.dumps([])
        self.semester = semester
        self.year = year

    def add_course(self, course):
        courses = json.loads(self.courses_data)
        courses.append(course_info)
        self.courses_data = json.dumps(courses)

    def get_json(self):
        return {
            'planId': self.planId,
            'studentId': self.studentId,
            'courses': json.loads(self.courses_data),
            'semester': self.semester,
            'year': self.year
        }