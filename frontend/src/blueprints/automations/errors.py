from flask import session, render_template, redirect, url_for, flash, abort
from functools import wraps

from src.blueprints.auth.forms.auth_forms import LoginForm
from src.repositories import auth_repository


def abort(error_code):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            result = f(*args, **kwargs)

            if result == error_code:
                error_template = f'webui/{error_code}.html'
                return render_template(error_template)

            return result

        return decorated_function

    return decorator
