from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.fields.html5 import EmailField


class RegisterForm(FlaskForm):
    email = EmailField('Email', render_kw={'class': 'form-control'})
    username = StringField('Username', render_kw={'class': 'form-control'})
    password = PasswordField('Password', render_kw={'class': 'form-control'})
    confirm_password = PasswordField('Confirm Password', render_kw={'class': 'form-control'})
    submit = SubmitField('Register', render_kw={'class': 'form-control'})


class LoginForm(FlaskForm):
    username = StringField('Username', render_kw={'class': 'form-control'})
    password = PasswordField('Password', render_kw={'class': 'form-control'})
    remember_me = BooleanField('Remember me', render_kw={'class': 'form-control'})
    submit = SubmitField('Login', render_kw={'class': 'form-control'})