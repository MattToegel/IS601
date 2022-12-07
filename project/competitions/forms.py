from flask_wtf import FlaskForm
from wtforms import StringField, HiddenField, IntegerField, SubmitField, IntegerRangeField
from wtforms.validators import DataRequired, Length, Optional, NumberRange, NumberRange
from wtforms.validators import ValidationError

# trick to pass javascript from Form definition to client-side version of rendered form
render_dict = {
    "onInput":"""
        /* get form */
        let form = document.forms[0];
        /* get hidden payout options */
        let po = form.payout_options;
        /* get place payout choices */
        let fp = form.fp.value;
        let sp = form.sp.value;
        let tp = form.tp.value;
        /* set as csv of data */
        po.value = `${fp},${sp},${tp}`;
       /* visual updates */
       let label = this.parentNode.querySelector('label');
       let v = this.value;
       label.innerText = label.innerText.split('-')[0] + `- ${v}`;
    """
}
class CompForm(FlaskForm):
    id = HiddenField("id", validators=[Optional()])
    title = StringField("title", validators=[DataRequired(), Length(min=3, max=240)])
    min_participants = IntegerField("min participants", validators=[NumberRange(min=3)])
    join_cost = IntegerField("join cost", validators=[NumberRange(min=1)])
    fp = IntegerRangeField("first place payout-", render_kw=render_dict, validators=[NumberRange(min=0, max=100)])
    sp = IntegerRangeField("second place payout-",render_kw=render_dict,validators=[NumberRange(min=0, max=100)])
    tp = IntegerRangeField("third place payout-", render_kw=render_dict,validators=[NumberRange(min=0, max=100)])
    payout_options = StringField("payout options", render_kw={"readonly":True})
    starting_reward = IntegerField("starting reward", validators=[NumberRange(min=1)])
    duration = IntegerField("duration", validators=[NumberRange(min=3)])
    min_score = IntegerField("min. score", validators=[NumberRange(min=1)])
    
    # TODO set via JS
    def validate_payout_options(form, field):
        print("validating", field)
        if not field.data or len(field.data) == 0:
            raise ValidationError("Must apply payout choices")
        total = int(form.fp.data) + int(form.sp.data) + int(form.tp.data)
        if total != 100:
            raise ValidationError("First, Second, Third place must total to 100")
    submit = SubmitField("Save")
