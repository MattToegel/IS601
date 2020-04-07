
from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField, HiddenField, validators
from wtforms.validators import InputRequired
from wtforms_alchemy import model_form_factory

from app import db
from core.models import Purchase

BaseModelForm = model_form_factory(FlaskForm)


class ModelForm(BaseModelForm):
    @classmethod
    def get_session(self):
        return db.session


class PurchaseForm(ModelForm):
    class Meta:
        model = Purchase
    id = HiddenField('id', [validators.optional()])
    cost = IntegerField('Cost', [InputRequired()], render_kw={'class': 'form-control', 'readonly': 'readonly'})
    submit = SubmitField('Purchase', render_kw={'class': 'form-control btn btn-primary'})