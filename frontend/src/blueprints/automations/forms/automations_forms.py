from flask_wtf import FlaskForm
from wtforms.fields import StringField, SubmitField, PasswordField, HiddenField, TextAreaField
from wtforms.validators import InputRequired, Email


class AutomationForm(FlaskForm):
    uuid = HiddenField('UUID')
    name = StringField('Nome',
                       validators=[
                           InputRequired(message='Campo NOME é obrigatório')
                       ]
                       )
    description = TextAreaField('Descrição',
                                validators=[
                                    InputRequired(message='Campo DESCRIÇÃO é obrigatório')
                                ]
                                )
    acronym = StringField('Sigla',
                          validators=[
                              InputRequired(message='Campo SIGLA é obrigatório')
                          ]
                          )
    submit = SubmitField('Salvar')

