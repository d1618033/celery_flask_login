import pytest
from celery_flask_login import current_user
import celery_flask_login
from flask_login import LoginManager, UserMixin, login_user
from dataclasses import dataclass
from flask import Flask, jsonify


@dataclass
class User(UserMixin):
    id: str


@pytest.fixture
def flask_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "secret!"
    app.config["TESTING"] = True
    return app


@pytest.fixture
def login_manager(flask_app):
    login_manager = LoginManager()
    login_manager.init_app(flask_app)
    login_manager.user_loader(User)
    return login_manager


@pytest.fixture
def flask_client(flask_app):
    return flask_app.test_client()


def test_basic_task(celery_app, celery_worker, flask_app, flask_client, login_manager):
    celery_flask_login.setup(User)

    @celery_app.task
    def echo(x, y, z):
        return {"x": x, "y": y, "z": z, "user_id": current_user.id if current_user else None}

    celery_worker.reload()

    @flask_app.route("/")
    def index():
        login_user(User(id="dave"))
        return jsonify({"result": echo.delay(1, 2, z=5).get(timeout=600)})

    assert flask_client.get("/").json["result"] == {
        "x": 1,
        "y": 2,
        "z": 5,
        "user_id": "dave",
    }
