from functools import wraps
from flask import render_template, redirect, url_for, flash
from flask_login import current_user


def required_roles(*roles):
    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            #  Checks if the user is anonymous
            if not current_user.is_authenticated:
                # Checks if function is made for anonymous users/If anonymous isn't allowed we send them
                # back to the login page
                if 'anonymous' not in roles:
                    flash('Please log in to access this page')
                    return redirect(url_for('users.login'))
            # If the user isn't allowed to access the page, we send him to the 403 Forbidden Error page
            elif current_user.role not in roles:
                return render_template('errors/403.html')

            return f(*args, **kwargs)

        return wrapped

    return wrapper