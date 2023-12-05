import os
from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, current_user, login_user
from flask_uploads import DOCUMENTS, IMAGES, TEXT, UploadSet, configure_uploads
from flask_cors import CORS
from werkzeug.utils import secure_filename
from werkzeug.datastructures import  FileStorage
from datetime import timedelta

#from App.database import init_db
from App.database import db
from App.config import config

from App.controllers import (
    setup_jwt,
    setup_flask_login
)

from App.models.user import User
from App.models.courses import Course
from App.models.program import Program
from App.models.staff import Staff
from App.models.student import Student

from App.views import views

from App.controllers.user import create_user, get_user, get_user_by_username
from App.controllers.staff import create_staff, get_staff_by_id, verify_staff
from App.controllers.student import create_student, get_student, verify_student
from App.controllers.courses import create_course, get_course_by_courseCode
from App.controllers.program import create_program, get_program_by_name, get_all_courses


def add_views(app):
    for view in views:
        app.register_blueprint(view)


def configure_app(app, config, overrides):
    for key, value in config.items():
        if key in overrides:
            app.config[key] = overrides[key]
        else:
            app.config[key] = config[key]


def create_app(config_overrides={}):
    app = Flask(__name__, static_url_path='/static')
    configure_app(app, config, config_overrides)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.config['SEVER_NAME'] = '0.0.0.0'
    app.config['PREFERRED_URL_SCHEME'] = 'https'
    app.config['UPLOADED_PHOTOS_DEST'] = "App/uploads"
    CORS(app)
    photos = UploadSet('photos', TEXT + DOCUMENTS + IMAGES)
    configure_uploads(app, photos)
    add_views(app)
    db.init_app(app)
    #init_db(app)
    setup_jwt(app)
    setup_flask_login(app)


    @app.route('/signup')
    def signup():
        return render_template('signup.html')


    @app.route('/signup', methods=['POST'])
    def handle_signup():
        if request.method == 'POST':
            # Retrieve form data
            username = request.form.get('username')
            password = request.form.get('password')
            user_type = request.form['user_type']

            create_user(username, password)

            if user_type == 'student':
                #create_student("id", password, username, "-")
                new_student = Student(username=username, password=password, name=username, program_id="-")
                db.session.add(new_student)

                # Redirect to a user dashboard
                return redirect(url_for('student_dashboard'))

            elif user_type == 'staff':
                #create_staff(password, "id", username)
                new_staff = Staff(password=password, staff_id=username, name=username)
                db.session.add(new_staff)
                
                # Redirect to a user dashboard
                return redirect(url_for('staff_dashboard'))

        # Handle GET requests or form submission failure
        return render_template('signup.html')
    

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            # Retrieve form data
            username = request.form.get('username')
            password = request.form.get('password')
            user_type = request.form['user_type']

            user = get_user_by_username(username)

            if user and user.check_password(password):
                
                if user_type == 'student':
                    # Log in the user and redirect to student dashboard if the student exists
                    #if verify_student(username):
                        login_user(user)
                        return redirect(url_for('student_dashboard'))

                elif user_type == 'staff':
                    # Log in the user and redirect to staff dashboard if the student exists
                    #if verify_staff(username):
                    login_user(user)
                    return redirect(url_for('staff_dashboard'))

        # Handle GET requests or form submission failure
        return render_template('login.html')


    @app.route('/staff-dashboard', methods=['GET', 'POST'])
    def staff_dashboard():

        if request.method == 'POST':

            if get_course_by_courseCode(request.form['course_code']):
                print(f"Course already exists")

            create_course(request.form['course_code'], request.form['course_name'], float(request.form['rating']), int(request.form['credits']), "-", int(request.form['semester']), int(request.form['year']))

        courses = Course.query.all()
        programs = Program.query.all()
        return render_template('staffDashboard.html', courses=courses, programs=programs)
    

    @app.route('/add_program', methods=['GET', 'POST'])
    def add_program():

        if request.method == 'POST':
            if get_program_by_name(request.form['program_name']):
                print(f"Program already exists")

            create_program(request.form['program_name'], int(request.form['core_credits']), int(request.form['elective_credits']), int(request.form['foun_credits']))

        courses = Course.query.all()
        programs = Program.query.all()
        return render_template('staffDashboard.html', courses=courses, programs=programs)


    @app.route('/student-dashboard')
    def student_dashboard():
        courses = Course.query.all()
        programs = Program.query.all()
        return render_template('studentDashboard.html', courses=courses, programs=programs)
    

    @app.route('/search_programs', methods=['GET'])
    def search_programs():
        query = request.args.get('program_query', '')

        # Perform the search for programs based on program name
        programs = Program.query.filter(Program.name.ilike(f"%{query}%")).all()

        # Fetch the list of courses
        courses = Course.query.all()
        #courses = get_all_courses(request.args.get('program_query', ''))

        return render_template('studentDashboard.html', courses=courses, programs=programs)


    @app.route('/search_courses', methods=['GET'])
    def search_courses():
        query = request.args.get('query', '')

        # Perform the search for courses based on course code or name
        courses = Course.query.filter(
            (Course.courseCode.ilike(f"%{query}%")) | (Course.courseName.ilike(f"%{query}%"))
        ).all()

        # Fetch the list of programs
        programs = Program.query.all()

        return render_template('studentDashboard.html', courses=courses, programs=programs)


    @app.route('/course_plan')
    def course_plan():
        # Fetch the list of courses
        courses = Course.query.all()
        return render_template('coursePlan.html', courses=courses)
    
    
    @app.route('/enroll_program/<program_id>', methods=['POST'])
    def enroll_program(program_id):
        """
        current_user = current_user.id

        # Check if the user is a student
        if isinstance(current_user, Student):
            # Find the program by ID
            program = Program.query.get(program_id)

            # Enroll the student in the program
            current_user.program_id = program.id
            db.session.commit()
        """
        return redirect(url_for('student_dashboard'))
    

    @app.route('/add_to_course_history/<course_code>', methods=['POST'])
    def add_to_course_history(course_code):
        
        """
        current_user = get_current_user()

        # Check if the user is a student
        if isinstance(current_user, Student):
            # Find the course by course code
            course = Course.query.filter_by(courseCode=course_code).first()

            # Add the course to the user's course history
            current_user.courses.append(course)
            db.session.commit()
        """

        return redirect(url_for('student_dashboard'))
    

    @app.route('/generate_course_plan', methods=['POST'])
    def generate_course_plan():
        plan_type = request.form.get('plan_type')

        """
        # Handle the selected plan type
        if plan_type == 'fastest_graduation':
            
        elif plan_type == 'easy_courses':
            
        elif plan_type == 'prioritize_electives':
           

        """

        # Render the appropriate template for the generated course plan
        return render_template('coursePlan.html')
    

    app.app_context().push()
    return app
