from collections import OrderedDict
from flask_wtf import FlaskForm
from wtforms.fields import (StringField, SubmitField, HiddenField,
                            TextAreaField, IntegerField, SelectField,
                            DateField, DateTimeField, BooleanField, FloatField,
                            )
from wtforms.validators import InputRequired, DataRequired, Email


def create_dynamic_fields(fields):
    dynamic_fields = {}
    for field in fields:
        field_name = field['name']
        field_alias = field['alias'].upper()
        is_required = field['required']

        if field['type'] == 'integer':
            field_class = IntegerField
        elif field['type'] == 'float':
            field_class = FloatField
        elif field['type'] == 'boolean':
            field_class = BooleanField
        elif field['type'] == 'date':
            field_class = DateField
        else:
            field_class = StringField

        if is_required:
            validators = [
                InputRequired(message='Campo {} é obrigatório'.format(field_alias))
            ]
        else:
            validators = []

        if field['type'] == 'email':
            validators.append(Email(message='Formato do e-mail invalido'))

        dynamic_fields[field_name] = field_class(field_alias, validators=validators)

    return dynamic_fields

class ItemForm(FlaskForm):
    uuid = HiddenField('UUID')
    submit = SubmitField('Salvar')
