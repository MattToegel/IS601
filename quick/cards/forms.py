from flask_wtf import FlaskForm
from wtforms import IntegerField,SubmitField, StringField, TextAreaField, SelectField, IntegerField
from wtforms.validators import DataRequired, Length, InputRequired

class CardFetchForm(FlaskForm):
    page = IntegerField("Page", default=1)
    page_size = IntegerField("Page Size", default=10)
    submit = SubmitField("Fetch")

class CardForm(FlaskForm):
    name = StringField("Name")
    text = TextAreaField("Text")
    flavor_text = TextAreaField("Flavor Text")
    mana_cost = IntegerField("Mana Cost")
    rarity = SelectField("Rarity")
    card_class = SelectField("Card Class")
    card_type = SelectField("Card Type")
    card_set = SelectField("Card Set")
    spell_school = SelectField("Spell School")
    submit = SubmitField("Save")

class CardSearchForm(FlaskForm):
    class Meta:
        # This overrides the value from the base form.
        csrf = False
    name = StringField("Name")
    text = TextAreaField("Text")
    mana_cost = IntegerField("Mana Cost")
    rarity = SelectField("Rarity")
    card_class = SelectField("Card Class")
    card_type = SelectField("Card Type")
    card_type = SelectField("Card Set")
    spell_school = SelectField("Spell School")
    limit = IntegerField("Limit", default=10)
    sort = SelectField("Sort")
    order = SelectField("Order", choices=[("asc","+"), ("desc","-")])
    submit = SubmitField("Filter")