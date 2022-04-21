from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, SubmitField
from wtforms.validators import DataRequired


class CompetitionForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    min_participants = IntegerField("Min Participants", validators=[DataRequired()])
    join_cost = IntegerField("Join Cost", validators=[DataRequired()])
    payout = SelectField("Payout", choices=[('100,0,0', '100,0,0'),
                                            ('80,20,10', '80,20,10'),
                                            ('70,30,10', '70,30,10')])
    starting_reward = IntegerField("Starting Reward", validators=[DataRequired()])
    duration = IntegerField("Duration", validators=[DataRequired()])
    min_score = IntegerField("Min. Score", validators=[DataRequired()])
    submit = SubmitField('Create Competition')
