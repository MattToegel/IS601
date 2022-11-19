from flask_wtf import FlaskForm
from wtforms import HiddenField


class GameForm(FlaskForm):
    # shared form that groups most of our validations together to reduce repetition
    score = HiddenField("score")
