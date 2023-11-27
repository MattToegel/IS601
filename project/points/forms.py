from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField

class ChangePointsForm(FlaskForm):
    username = StringField("username")
    amount = IntegerField("Amount", )
    submit = SubmitField("Change Points")