from .models import *
from .views import *
from .controllers import *
from .main import *

from App.models.user import User
from App.controllers import login_manager

@login_manager.user_loader
def load_user(user_id):
    # Load the user from the database using the user ID
    return User.query.get(int(user_id))