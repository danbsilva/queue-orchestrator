from flask import current_app, session, render_template, redirect, url_for
from functools import wraps
from jose import jwt

from src.models import Usuario

from src.blueprints.auth.forms.auth_forms import LoginForm


def verify_login(f):

    @wraps(f)
    def decorated(*args, **kwargs):

        form = LoginForm()
        access_token = None

        try:
            access_token = session.get('token')
        except:
            ...

        if not access_token:
            form.form_errors.append('Necessário fazer login para acessar a página solicitada')
            return redirect(url_for('auth.login'))

        try:
            carga = jwt.decode(access_token, current_app.config['SECRET_KEY'],
                               algorithms=[current_app.config['ALGORITHM']])
            current_user = Usuario.query.filter_by(id=carga['id']).first()
        except:
            form.form_errors.append('Necessário fazer login para acessar a página solicitada')
            return redirect(url_for('auth.login'))

        return f(current_user, *args, **kwargs)

    return decorated
