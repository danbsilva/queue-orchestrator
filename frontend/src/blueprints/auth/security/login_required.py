from flask import session, render_template, redirect, url_for, flash
from functools import wraps

from src.blueprints.auth.forms.auth_forms import LoginForm
from src.repositories import auth_repository


def verify_login(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'token' not in session:
            return redirect(url_for('auth.login'))

        return f(*args, **kwargs)

    return decorated_function
