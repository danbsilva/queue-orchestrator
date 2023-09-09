from flask_wtf import FlaskForm
from wtforms.fields import StringField, SubmitField, PasswordField, HiddenField, TextAreaField, IntegerField
from wtforms.validators import InputRequired, Email


class StepForm(FlaskForm):
    uuid = HiddenField('UUID')
    name = StringField('Nome',
                       validators=[
                           InputRequired(message='Campo NOME é obrigatório')
                       ]
                       )
    description = TextAreaField('Descrição',
                                validators=[
                                    InputRequired(message='O campo DESCRIÇÃO é obrigatório')
                                ]
                                )
    step = IntegerField('Passo',
                        validators=[
                            InputRequired(message='Campo PASSO é obrigatório')
                        ]
                        )
    topic = StringField('Tópico',
                        validators=[
                            InputRequired(message='Campo TÓPICO é obrigatório')
                        ]
                        )
    try_count = IntegerField('Tentativas',
                             validators=[
                                 InputRequired(message='Campo TENTATIVAS é obrigatório')
                             ]
                             )
    submit = SubmitField('Salvar')

