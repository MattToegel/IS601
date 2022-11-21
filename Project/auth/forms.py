import email_validator
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError

# custom validator
class EmailOrUsernameValidator(object):
    def __init__(self, message=None):
        if not message:
            message = "Username or email is invalid"
        self.message = message

    def __call__(self, form, field):
        if "@" in field.data:
            try:
                email_validator.validate_email(field.data)
            except Exception as e:
                print(e)
                self.message = "Invalid Email {}".format(e)
                field.errors.append(self.message)
                return False

        else:
            if not len(field.data) > 2:  # basic/sample username validation
                self.message = "Invalid username"
                field.errors.append(self.message)
                return False
        return True


class RegistrationForm(FlaskForm):
    username = StringField('username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password1 = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password1')])
    submit = SubmitField('Register')


class LoginForm(FlaskForm):
    email = StringField('Email/Username',
                        validators=[DataRequired(),
                                    EmailOrUsernameValidator()])  # see validate() to allow username OR email validation
    password = PasswordField('Password', validators=[DataRequired()])
    # remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class ProfileForm(FlaskForm):
    username = StringField('username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    current_password = PasswordField('Current Password', validators=[])
    password1 = PasswordField('New Password', validators=[])
    password2 = PasswordField('Confirm new Password', validators=[EqualTo('password1')])
    submit = SubmitField('Save Profile')
