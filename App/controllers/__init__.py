from .user import *
from .auth import *
from .courses import *
from .program import *
from .staff import *
from .student import *
from .prerequistes import *
from .programCourses import *
from .studentCourseHistory import *
from .coursePlanCourses import *
from .coursesOfferedPerSem import *
from .coursePlan import *

from flask_login import LoginManager

login_manager = LoginManager()

def setup_flask_login(app):
    login_manager.init_app(app)
    login_manager.login_view = 'login'