from flask_wtf import FlaskForm
from wtforms.fields import StringField, SubmitField, PasswordField, HiddenField, TextAreaField
from wtforms.validators import InputRequired, Email


class AutomationForm(FlaskForm):
    uuid = HiddenField('UUID')
    name = StringField('Nome', validators=[InputRequired()])
    description = TextAreaField('Descrição', validators=[InputRequired()])
    acronym = StringField('Sigla', validators=[InputRequired()])
    submit = SubmitField('Salvar')

