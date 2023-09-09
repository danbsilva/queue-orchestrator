from flask_wtf import FlaskForm
from wtforms.fields import StringField, SubmitField, PasswordField
from wtforms.validators import InputRequired, Email


class LoginForm(FlaskForm):
    email = StringField('E-mail',
                        [
                            InputRequired(message='O campo E-MAIL é obrigatório'),
                            Email(message='Formato do e-mail invalido')
                        ]
                        )
    password = PasswordField('Senha',
                             [
                                 InputRequired(message='O campo SENHA é obrigatório')
                             ]
                             )
    logar = SubmitField('Entrar')

