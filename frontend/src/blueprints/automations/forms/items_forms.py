from flask_wtf import FlaskForm
from wtforms.fields import StringField, SubmitField, PasswordField, HiddenField, TextAreaField, IntegerField
from wtforms.validators import InputRequired, Email


class StepForm(FlaskForm):
    uuid = HiddenField('UUID')
    name = StringField('Nome', validators=[InputRequired()])
    description = TextAreaField('Descrição', validators=[InputRequired()])
    step = IntegerField('Passo', validators=[InputRequired()])
    topic = StringField('Tópico', validators=[InputRequired()])
    try_count = IntegerField('Tentativas', validators=[InputRequired()])
    submit = SubmitField('Salvar')

