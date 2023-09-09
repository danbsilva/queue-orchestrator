from flask_wtf import FlaskForm
from wtforms.fields import (
    StringField, SubmitField, PasswordField, HiddenField,
    TextAreaField, IntegerField, SelectField, BooleanField
                            )
from wtforms.validators import InputRequired, Email


class FieldForm(FlaskForm):
    uuid = HiddenField('UUID')
    name = StringField('Nome',
                       validators=[
                           InputRequired(message='Campo NOME é obrigatório')
                       ]
                       )
    alias = StringField('Apelido',
                        validators=[
                            InputRequired(message='Campo APELIDO é obrigatório')
                        ]
                        )
    description = TextAreaField('Descrição',
                                validators=[
                                    InputRequired(message='Campo DESCRIÇÃO é obrigatório')
                                ]
                                )
    type = SelectField('Tipo',
                       choices=[
                            ('string', 'Texto'),
                            ('integer', 'Inteiro'),
                            ('float', 'Decimal'),
                            ('boolean', 'Verdadeiro/Falso'),
                            ('date', 'Data'),
                            ('datetime', 'Data e hora'),
                            ('list', 'Lista'),
                            ('dict', 'Dicionário'),
                            ('url', 'URL'),
                            ('email', 'E-mail')
                        ]
                       )
    required = BooleanField('Obrigatório')
    submit = SubmitField('Salvar')

