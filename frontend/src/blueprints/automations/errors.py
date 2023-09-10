from flask import render_template
from functools import wraps


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
