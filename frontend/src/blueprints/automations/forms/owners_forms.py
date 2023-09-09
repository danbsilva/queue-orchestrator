from flask_wtf import FlaskForm
from wtforms.fields import SelectField, SubmitField
from wtforms.validators import InputRequired


class OwnerForm(FlaskForm):
    owner = SelectField('Owners', coerce=str)
    submit = SubmitField('Salvar')

