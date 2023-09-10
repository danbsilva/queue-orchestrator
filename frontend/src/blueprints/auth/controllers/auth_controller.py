from flask import render_template, request, session
from src.blueprints.auth.forms.auth_forms import LoginForm

from src.repositories import auth_repository
from src.blueprints.auth.security import login_required
from src.helpers import convert_error_to_tuple


def login():
    errors = []
    form = LoginForm(request.form)
    if request.method == 'POST':
        if form.validate_on_submit():
            args = form.data
            args.pop('salvar', None)
            args.pop('csrf_token', None)

            response, code = auth_repository.login(args['email'], args['password'])
            if code == 200:
                session['token'] = response['token']
                session['uuid'] = response['user']['uuid']
                session['username'] = response['user']['username']
                session['name'] = response['user']['name']
                session['email'] = response['user']['email']
                session['is_admin'] = response['user']['is_admin']

                return 'webui.home', code

            errors = convert_error_to_tuple(response)
            return errors, code

        else:
            errors = errors + list(form.errors.items())
            return errors, 400

    return render_template('auth/login.html', form=form)


@login_required.verify_login
def logout():
    response, code = auth_repository.logout()
    if code == 200:
        session.pop('token', None)
        session.pop('uuid', None)
        session.pop('username', None)
        session.pop('name', None)
        session.pop('email', None)
        session.pop('is_admin', None)

        return 'auth.login', code

    errors = convert_error_to_tuple(response)
    return errors, code


