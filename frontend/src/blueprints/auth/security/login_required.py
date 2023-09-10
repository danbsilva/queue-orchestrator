from flask import session, redirect, url_for
from functools import wraps


def verify_login(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'token' not in session:
            return redirect(url_for('auth.login'))

        return f(*args, **kwargs)

    return decorated_function
