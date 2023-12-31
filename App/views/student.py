from flask import Blueprint, render_template, jsonify, request, send_from_directory, flash, redirect, url_for
from flask_jwt_extended import jwt_required, current_user as jwt_current_user
from flask_login import current_user, login_required
import json
from.index import index_views

from App.controllers import (
    create_user,
    jwt_authenticate, 
    get_all_users,
    get_all_users_json,
    jwt_required,
    create_student,
    get_program_by_name,
    get_student_by_id,
    get_course_by_courseCode,
    addCoursetoHistory,
    getCompletedCourseCodes,
    generator,
    addCourseToPlan,
    verify_student,
    getStudentCourseHistory,
    updateScore,
    getStudentCourseHistoryJSON,
    course_offered,
    create_CoursePlan,
    getCoursePlan,
)

student_views = Blueprint('student_views', __name__, template_folder='../templates')

##Create student
@student_views.route('/student', methods=['POST'])
def create_student_route():
    student_id = request.json['student_id']
    password = request.json['password']
    name = request.json['name']
    programname = request.json['programname']

    if not all([student_id, password, name, programname]):
        return jsonify({'Error': 'Missing required fields. Please provide student id, password, name, and program name.'}), 400

    student = get_student_by_id(student_id)
    if student:
        return jsonify({'Error': 'Student id found'}), 400
    
    program = get_program_by_name(programname)
    if not program:
        return jsonify({'Error': 'Incorrect program name'}), 400

    create_student(student_id, password, name, programname)
    return jsonify({'Success!': f"user {student_id} created"}), 201
    
##Add course to course history

@student_views.route('/student/add_course', methods=['POST'])
@login_required
def add_course_to_student_route():
    student_id = request.json['student_id']
    course_code = request.json['course_code']
    score = request.json['score']

    username=current_user.username
    if not verify_student(username):    #verify that the user is logged in
        return jsonify({'message': 'You are unauthorized to perform this action. Please login with Student credentials.'}), 401
    
    if not student_id or not course_code:
        return jsonify({'Error': 'Missing required fields'}), 400

    # Check if the student and course exist
    student = get_student_by_id(student_id)
    course = get_course_by_courseCode(course_code)

    if not student:
        return jsonify({'Error': 'Student not found'}), 400
    if not course:
        return jsonify({'Error': 'Course not found'}), 400

    # Check if the course is already in the student's completed courses
    completed_courses = getCompletedCourseCodes(student_id)
    if course_code in completed_courses and score < 50:
        updateScore(student_id, course_code, score)
        return jsonify({'Success': 'Course score updated'}), 200
    elif course_code in completed_courses and score >= 50:
        return jsonify({'Error': 'Course already completed'}), 400
        
    addCoursetoHistory(student_id, course_code, score)
    return jsonify({'Success!': f"Course {course_code} added to student {student_id}'s course history"}), 200


@student_views.route('/student/create_student_plan', methods=['POST'])
@login_required
def create_student_plan_route():
    student_id = request.json['student_id']
    semester = request.json['semester']
    year = request.json['year']

    username=current_user.username
    if not verify_student(username):    #verify that the student is logged in
        return jsonify({'message': 'You are unauthorized to perform this action. Please login with Student credentials.'}), 401
    
    student = get_student_by_id(student_id)
    if not student:
        return jsonify({'Error': 'Student not found'}), 400

    plan = getCoursePlan(student_id, semester, year)
    if plan:
        return jsonify({'Error': 'Course plan already exists'}), 400

    plan = create_CoursePlan(student_id, semester, year)
    return jsonify({'Success!': f"Course plan created for student {student_id}"}), 201

@student_views.route('/student/get_student_plan', methods=['GET'])
@login_required
def get_student_plan_route():
    student_id = request.args.get('student_id')
    semester = request.args.get('semester')
    year = request.args.get('year')

    username=current_user.username
    if not verify_student(username):    #verify that the student is logged in
        return jsonify({'message': 'You are unauthorized to perform this action. Please login with Student credentials.'}), 401

    if username != student_id:
        return jsonify({'Error': 'Unauthorized to view other student\'s course plan'}), 403

    student = get_student_by_id(student_id)
    if not student:
        return jsonify({'Error': 'Student not found'}), 400

    plan = getCoursePlan(student_id, semester, year)
    if not plan:
        return jsonify({'Error': 'Course plan not found'}), 400

    courses_data = json.loads(plan.courses_data) if plan.courses_data else []
    return jsonify({'Success!': f"Course plan for student {student_id} in Semester {semester} {year}", "courses" :courses_data}), 200

##Add course plan 

@student_views.route('/student/populate_student_plan', methods=['POST'])
@login_required
def populate_student_plan_route():
    data = request.json
    student_id = data.get('student_id')
    command = data.get('command')
    semester = data.get('semester')
    year = data.get('year')
    
    #return jsonify({"Student ID": student_id, "Command": command, "Semester": semester, "Year": year}), 200

    username=current_user.username
    if not verify_student(username):    #verify that the student is logged in
        return jsonify({'message': 'You are unauthorized to perform this action. Please login with Student credentials.'}), 401
    
    student = get_student_by_id(student_id)

    if not student:
        return jsonify({'Error': 'Student not found'}), 400
    
    if username != student_id:
        return jsonify({'Error': 'Unauthorized to view other student\'s course plan'}), 403
    
    valid_command = ["electives", "easy", "fastest"]

    if command in valid_command:
        courses = generator(student, command)
        return jsonify({'Success!': f"{command} plan added to student {student_id} ", "courses" : courses}), 200
    else:
        course = get_course_by_courseCode(command)
        if course==None:
            return jsonify({'Error': 'Course not found'}), 400

        offered = course_offered(course.courseCode, semester, year)
        if not offered:
            return jsonify({'Error': 'Course not offered in this semester or year'}), 400

        if course and offered:
            plan = getCoursePlan(student_id, semester, year)
            message=addCourseToPlan(student, command, plan.semester, plan.year)
            return jsonify(message), 200
        else:
            return jsonify("Invalid command. Please enter 'electives', 'easy', 'fastest', or a valid/offered course code."), 400

##Get student course history
@student_views.route('/student/all_course_history', methods=['GET'])
@login_required
def get_all_student_course_history_route():
    username = current_user.username
    if not verify_student(username):
        return jsonify({'message': 'You are unauthorized to perform this action. Please login with Student credentials.'}), 401

    requested_student_id = request.args.get('student_id')
    if not requested_student_id:
        return jsonify({'Error': 'Student ID is required'}), 400 

    if str(requested_student_id) != username:
        return jsonify({'Error': 'Unauthorized to view other student\'s course history'}), 403

    student = get_student_by_id(requested_student_id)
    if not student:
        return jsonify({'Error': 'Student not found'}), 400

    courses = getStudentCourseHistoryJSON(requested_student_id)
    return jsonify({'Success!': f"Student {requested_student_id} course history", "courses" : courses}), 200


        
    
    
