from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, SubmitField, StringField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional
from wtforms.validators import ValidationError

def is_valid_username(username):
    import re
    r = re.fullmatch("^[a-z0-9_-]{2,30}$", username)
    print("re",r)
    if not r:
        print("validation errr")
        raise ValidationError("Invalid username format")

class AuthForm(FlaskForm):
    # shared form that groups most of our validations together to reduce repetition
    username = StringField("username", validators=[DataRequired(), Length(2, 30)])
    email = EmailField("email", validators=[DataRequired(), Email()])
    password = PasswordField("password", validators=[DataRequired(), EqualTo('confirm', message='Passwords must match'), Length(8)])
    confirm = PasswordField("confirm", validators=[DataRequired(),  EqualTo('password', message='Passwords must match'),Length(8)])
    def validate_username(form, field):
        print("checking ", field.data)
        is_valid_username(field.data)
class RegisterForm(AuthForm):
    submit = SubmitField("Register")

class LoginForm(AuthForm):
    email = StringField("email or username", validators=[DataRequired()]) #EmailField("email", validators=[DataRequired(), Email()])
    submit = SubmitField("Login")
    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__( *args, **kwargs)
        if len(self.password.validators) >= 2:
            self.password.validators.pop(1)
        del self.confirm
        del self.username
        
    # https://wtforms.readthedocs.io/en/stable/validators/#custom-validators
    def validate_email(form, field):
        email = field.data
        from email_validator import validate_email
        if "@" in email:
            try:
                validate_email(email)
            except:
                raise ValidationError("Invalid email address")
        else:
            is_valid_username(email)
        return True
                
class ProfileForm(AuthForm):
    current_password = PasswordField("current password", validators=[Optional()])
    # https://wtforms.readthedocs.io/en/3.0.x/forms/#form-inheritance
    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__( *args, **kwargs)
        # replace required validator with optional
        self.password.validators[0]=Optional()
        self.confirm.validators[0]=Optional()
    submit = SubmitField("Update")