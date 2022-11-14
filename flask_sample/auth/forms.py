from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, SubmitField, StringField
from wtforms.validators import DataRequired, Email, InputRequired, EqualTo, Length, Optional

class RegisterForm(FlaskForm):
    username = StringField("username", validators=[DataRequired(), Length(2, 30)])
    email = EmailField("email", validators=[DataRequired(), Email()])
    password = PasswordField("password", validators=[InputRequired(), EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField("confirm", validators=[DataRequired()])
    submit = SubmitField("Register")

class LoginForm(FlaskForm):
    email = StringField("email or username", validators=[DataRequired()]) #EmailField("email", validators=[DataRequired(), Email()])
    password = PasswordField("password", validators=[InputRequired()])
    submit = SubmitField("Login")

class ProfileForm(FlaskForm):
    username = StringField("username", validators=[DataRequired(), Length(2, 30)])
    email = EmailField("email", validators=[DataRequired(), Email()])
    current_password = PasswordField("current password", validators=[Optional()])
    password = PasswordField("password", validators=[Optional(), EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField("confirm", validators=[Optional(), EqualTo("password")])
    submit = SubmitField("Update")