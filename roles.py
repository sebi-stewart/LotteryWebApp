from functools import wraps
from flask import render_template
from flask_login import current_user


def required_roles(*roles):
    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):

            if current_user.role not in roles:
                return render_template('errors/403.html')

            return f(*args, **kwargs)

        return wrapped

    return wrapper