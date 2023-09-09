from marshmallow import Schema, fields, validate
from src import messages


class UserPostSchema(Schema):
    name = fields.String(
        required=True,
        error_messages={
            'required': messages.FIELD_IS_REQUIRED
        }
    )
    email = fields.Email(
        required=True,
        error_messages={
            'required': messages.FIELD_IS_REQUIRED,
            'invalid': messages.FIELD_IS_EMAIL_INVALID
        }
    )
    password = fields.String(
        required=True,
        error_messages={
            'required': messages.FIELD_IS_REQUIRED
        },
        validate=[
            validate.Length(min=6, max=12, error=messages.FIELD_BETWEEN_6_AND_12)
        ]
    )

    class Meta:
        ordered = True


class UserGetSchema(Schema):
    uuid = fields.String()
    name = fields.String()
    username = fields.String()
    email = fields.Email()
    email_sent = fields.Bool()
    email_valid = fields.Bool()
    is_admin = fields.Bool()

    class Meta:
        ordered = True


class UserPatchSchema(Schema):
    name = fields.String(
        required=False
    )
    username = fields.String(
        required=False,
        validate=[
            validate.Length(min=6, max=12, error=messages.FIELD_BETWEEN_6_AND_12)
        ]
    )
    email = fields.Email(
        required=False,
        error_messages={
            'invalid': messages.FIELD_IS_EMAIL_INVALID
        }
    )

    class Meta:
        ordered = True


class UserLoginSchema(Schema):
    email = fields.Email(
        required=True,
        error_messages={
            'required': messages.FIELD_IS_REQUIRED,
            'invalid': messages.FIELD_IS_EMAIL_INVALID
        }
    )
    password = fields.String(
        required=True,
        error_messages={
            'required': messages.FIELD_IS_REQUIRED
        }
    )

    class Meta:
        ordered = True


class UserChangePasswordSchema(Schema):
    password = fields.String(
        required=True,
        error_messages={
            'required': messages.FIELD_IS_REQUIRED
        },
        validate=[
            validate.Length(min=6, max=12, error=messages.FIELD_BETWEEN_6_AND_12)
        ]
    )
    new_password = fields.String(
        required=True,
        error_messages={
            'required': messages.FIELD_IS_REQUIRED
        },
        validate=[
            validate.Length(min=6, max=12, error=messages.FIELD_BETWEEN_6_AND_12)
        ]
    )
    confirm_new_password = fields.String(
        required=True,
        error_messages={
            'required': messages.FIELD_IS_REQUIRED
        },
        validate=[
            validate.Length(min=6, max=12, error=messages.FIELD_BETWEEN_6_AND_12)
        ]
    )

    class Meta:
        ordered = True


class ForgotPasswordSchema(Schema):
    email = fields.Email(
        required=True,
        error_messages={
            'required': messages.FIELD_IS_REQUIRED,
            'invalid': messages.FIELD_IS_EMAIL_INVALID
        }
    )

    class Meta:
        ordered = True


class UserSendEmailValidationSchema(Schema):
    email = (fields.Email(
        required=True,
        error_messages={
            'required': messages.FIELD_IS_REQUIRED,
            'invalid': messages.FIELD_IS_EMAIL_INVALID
        }
    ))

    class Meta:
        ordered = True