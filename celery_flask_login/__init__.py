import werkzeug
import contextvars
from flask import has_request_context
from celery.signals import before_task_publish, task_prerun
from flask_login import current_user as flask_login_current_user


def setup(user_loader_func):
    @before_task_publish.connect(weak=False)
    def before_task_publish_handler(sender=None, headers=None, body=None, **kwargs):
        user = current_user
        headers.update(
            {
                "user_id": user.id if user else None,
            }
        )

    @task_prerun.connect(weak=False)
    def task_prerun_handler(task, task_id, args, kwargs, *_args, **_kwargs):
        user_id = task.request.user_id
        user = user_loader_func(id=user_id)
        _cv_current_user.set(user)


_cv_current_user = contextvars.ContextVar("current_user", default=None)


def get_current_user():
    if has_request_context():
        return flask_login_current_user
    else:
        return _cv_current_user.get()


current_user = werkzeug.local.LocalProxy(get_current_user)
