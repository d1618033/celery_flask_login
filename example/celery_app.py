"""
Demo app.
You can run this by running the following commands:

    # in one window:
    celery -A celery_app:celery_app worker -l INFO

    # in the other window:
    flask --app celery_app:flask_app run --reload

    # try it out with
    curl -H "username: dave" localhost:5000
"""


from celery import Celery
from flask import Flask, request
from dataclasses import dataclass
import logging
from flask_login import UserMixin, LoginManager, login_user
from celery_flask_login import current_user
import celery_flask_login

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)


flask_app = Flask(__name__)
flask_app.config["SECRET_KEY"] = "secret!"
login_manager = LoginManager()
login_manager.init_app(flask_app)


@login_manager.user_loader
@dataclass
class User(UserMixin):
    id: str


# celery code:

celery_app = Celery(__name__)
celery_flask_login.setup(flask_app)


@celery_app.task
def task_debug(*args, **kwargs):
    logger.info(f"OUTER User {current_user} ran task with {args} and {kwargs}")
    inner_task.delay(*args, **kwargs)


@celery_app.task
def inner_task(*args, **kwargs):
    logger.info(f"INNER: User {current_user} ran task with {args} and {kwargs}")


@flask_app.route("/")
def index():
    user = User(request.headers["username"])
    login_user(user)
    task_debug.delay(1, 2, x=4, y=5)
    return current_user.id
