from flask import render_template, request, redirect, url_for, session, flash
from src.blueprints.auth.forms.auth_forms import LoginForm

from src.repositories import auth_repository


def login():
    form = LoginForm(request.form)
    if request.method == 'POST':
        if form.validate_on_submit():
            args = form.data
            args.pop('salvar', None)
            args.pop('csrf_token', None)

            response, code = auth_repository.login(args['email'], args['password'])
            if code == 200:
                session['token'] = response['token']
                return redirect(url_for('webui.home'))
            else:
                flash(response['message'])

    return render_template('auth/login.html', form=form)


def logout():
    form = LoginForm()

    session['id'] = None
    session['nome'] = None
    session['email'] = None
    session['token'] = None

    flash('Você fez logout do sistema')

    return render_template('auth/login.html', form=form)

