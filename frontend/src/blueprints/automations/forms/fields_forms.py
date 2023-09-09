from flask_wtf import FlaskForm
from wtforms.fields import StringField, SubmitField, PasswordField, HiddenField, TextAreaField, IntegerField
from wtforms.validators import InputRequired, Email


class StepForm(FlaskForm):
    uuid = HiddenField('UUID')
    name = StringField('Nome', validators=[InputRequired(message='Nome é obrigatório')])
    description = TextAreaField('Descrição', validators=[InputRequired(message='Descrição é obrigatório')])
    step = IntegerField('Etapa', validators=[InputRequired(message='Etapa é obrigatório')])
    topic = StringField('Tópico', validators=[InputRequired(message='Tópico é obrigatório')])
    try_count = IntegerField('Tentativas', validators=[InputRequired(message='Tentativas é obrigatório')])
    submit = SubmitField('Salvar')

