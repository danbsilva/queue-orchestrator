from flask import render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash, generate_password_hash

from src.helpers.token_provider import create_token_jwt
from src.blueprints.auth.forms.auth_forms import LoginForm

from src.models import Usuario


def on_login(user):

    session['id'] = user.id
    session['nome'] = user.nome
    session['email'] = user.email
    session['token'] = create_token_jwt(user.id)


def login():
    form = LoginForm(request.form)
    if form.validate_on_submit():
        args = form.data
        args.pop('salvar', None)
        args.pop('csrf_token', None)

        user = Usuario.query.filter_by(email=form.data['email']).first()
        if not user:
            form.email.errors.append('E-mail não cadastrado')
            return render_template('auth/login.html', form=form)

        if check_password_hash(user.password, form.data['password']):
            on_login(user=user)
            return redirect(url_for('webui.index'))
        else:
            form.password.errors.append('Senha inválida')

    return render_template('auth/login.html', form=form)


def logout():
    form = LoginForm()

    session['id'] = None
    session['nome'] = None
    session['email'] = None
    session['token'] = None

    flash('Você fez logout do sistema')

    return render_template('auth/login.html', form=form)

