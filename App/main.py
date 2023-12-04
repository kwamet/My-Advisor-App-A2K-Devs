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

            new_user = User(username=username, password=password)
            user = User.query.filter_by(username=username).first()
            db.session.add(new_user)
            db.session.commit()

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

            # Perform login logic (e.g., validate credentials)
            user = User.query.filter_by(username=username).first()

            if user and user.check_password(password):
                # Log in the user
                login_user(user)
                # Redirect to a success page or another route
                return redirect(url_for('staff_dashboard'))

        # Handle GET requests or form submission failure
        return render_template('login.html')

    @app.route('/login/success')
    def login_success():
        return render_template('login_success.html')

    @app.route('/staff-dashboard')
    def staff_dashboard():
        return render_template('staffDashboard.html')

    app.app_context().push()
    return app