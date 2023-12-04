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

from App.views import views
from App.models.user import User
from App.models.courses import Course
from App.models.program import Program
from App.models.staff import Staff
from App.models.student import Student

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

            new_user = User(username=username, password=password)
            user = User.query.filter_by(username=username).first()
            db.session.add(new_user)
            db.session.commit()

            if user_type == 'student':
                new_student = Student(username=username, password=password, name=username, program_id="-")
                db.session.add(new_student)

                # Redirect to a user dashboard
                return redirect(url_for('student_dashboard'))

            elif user_type == 'staff':
                new_staff = Staff(password=password, staff_id=username, name=username)
                db.session.add(new_staff)
                
                # Redirect to a user dashboard
                return redirect(url_for('staff_dashboard'))


        # Handle GET requests or form submission failure
        return render_template('signup.html')
    
    def load_user(user_id):
    # Load the user from the database using the user ID
        return User.query.get(int(user_id))


    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            # Retrieve form data
            username = request.form.get('username')
            password = request.form.get('password')
            user_type = request.form['user_type']

            # Perform login logic (e.g., validate credentials)
            user = User.query.filter_by(username=username).first()

            if user and user.check_password(password):
                
                if user_type == 'student':
                    # Log in the user
                    login_user(user)
                    # Redirect to a student dashboard
                    return redirect(url_for('student_dashboard'))

                elif user_type == 'staff':
                    # Log in the user
                    login_user(user)
                    # Redirect to a staff dashboard
                    return redirect(url_for('staff_dashboard'))

        # Handle GET requests or form submission failure
        return render_template('login.html')

    @app.route('/staff-dashboard', methods=['GET', 'POST'])
    def staff_dashboard():

        if request.method == 'POST':
            course_code = request.form['course_code']
            course_name = request.form['course_name']
            credits = int(request.form['credits'])
            rating = float(request.form['rating'])
            semester = int(request.form['semester'])
            year = int(request.form['year'])

            new_course = Course(
                code=course_code,
                name=course_name,
                credits=credits,
                rating=rating,
                semester=semester,
                year=year
            )

            db.session.add(new_course)
            db.session.commit()

        courses = Course.query.all()
        programs = Program.query.all()
        return render_template('staffDashboard.html', courses=courses, programs=programs)
    
    @app.route('/add_program', methods=['GET', 'POST'])
    def add_program():

        if request.method == 'POST':
            program_name = request.form['program_name']
            core_credits = int(request.form['core_credits'])
            elective_credits = int(request.form['elective_credits'])
            foun_credits = int(request.form['foun_credits'])

            new_program = Program(
                name=program_name,
                core=core_credits,
                elective=elective_credits,
                foun=foun_credits
            )

            db.session.add(new_program)
            db.session.commit()

        courses = Course.query.all()
        programs = Program.query.all()
        return render_template('staffDashboard.html', courses=courses, programs=programs)

    @app.route('/student-dashboard')
    def student_dashboard():
        courses = Course.query.all()
        programs = Program.query.all()
        return render_template('studentDashboard.html', courses=courses, programs=programs)

    app.app_context().push()
    return app