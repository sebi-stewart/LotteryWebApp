from functools import wraps
from flask import render_template, redirect, url_for, flash
from flask_login import current_user


def required_roles(*roles):
    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            # Checks if user is anonymous
            if not current_user.is_authenticated:
                flash('Please log in to access this page')
                return redirect(url_for('users.login'))
            if current_user.role not in roles:
                return render_template('errors/403.html')

            return f(*args, **kwargs)

        return wrapped

    return wrapper