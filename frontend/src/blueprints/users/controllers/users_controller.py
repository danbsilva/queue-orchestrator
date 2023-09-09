from flask import render_template, request, redirect, url_for, session, flash
from src.blueprints.auth.forms.auth_forms import LoginForm

from src.repositories import auth_repository
from src.blueprints.auth.security import login_required


def login():
    form = LoginForm(request.form)
    if request.method == 'POST':
        if form.validate_on_submit():
            args = form.data
            args.pop('salvar', None)
            args.pop('csrf_token', None)

            response, code = auth_repository.login(args['email'], args['password'])
            print(response, code)
            if code == 200:
                session['token'] = response['token']
                response, code = auth_repository.me()
                print(response, code)
                if code == 200:
                    user = response['user']
                    session['uuid'] = user['uuid']
                    session['nome'] = user['name']
                    session['email'] = user['email']
                    session['username'] = user['username']
                    session['is_admin'] = user['is_admin']
                    session['is_active'] = user['is_active']
                    print(user)

                    return redirect(url_for('webui.home'))
            else:
                flash(response['message'], 'danger')

    return render_template('auth/login.html', form=form)


@login_required.verify_login
def logout():
    form = LoginForm()

    session['token'] = None
    session['uuid'] = None
    session['nome'] = None
    session['username'] = None
    session['email'] = None
    session['is_admin'] = None
    session['is_active'] = None

    flash('Você fez logout do sistema')

    return render_template('auth/login.html', form=form)

