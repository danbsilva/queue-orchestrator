from flask import render_template, request, redirect, url_for, session, flash
from src.blueprints.auth.forms.auth_forms import LoginForm

from src.repositories import users_repository
from src.blueprints.auth.security import login_required

@login_required.verify_login
def home():
    return render_template('webui/index.html')