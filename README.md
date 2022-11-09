# Celery Flask Login

For people who like celery and flask and logins

## Intro

Ever had that problem where you wanted to know the user that initiated a celery task
and just couldn't find a way to get that user info without passing it down a deeply nested function?

Well then this package is for you!


## Requirements

This package assumes you use flask and celery and flask_login for authentication

## Usage

```python

import celery_flask_login
from celery_flask_login import current_user
from celery import Celery

celery_app = Celery(__name__)
celery_flask_login.setup(User)

@celery_app.task
def task_debug(*args, **kwargs):
    logger.info(f"User {current_user} ran task with {args} and {kwargs}")
```

That's right, it's just that simple!


Only thing to note is that you should be using `current_user` from `celery_flask_login`
instead of from `flask_login` (it's a proxy to it)

