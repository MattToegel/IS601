from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, FieldList, FormField, SubmitField, validators, SelectField, HiddenField

class StockEntryForm(FlaskForm):
    symbol = StringField('Stock Symbol', [validators.Length(min=1, max=10)])
    shares = IntegerField('Shares', [validators.NumberRange(min=1)])

class BrokerForm(FlaskForm):
    name = StringField('Name', [validators.Length(min=1, max=255)])
    rarity = IntegerField('Rarity', [validators.NumberRange(min=1)], default=1)
    life = IntegerField('Life', [validators.NumberRange(min=0)], render_kw={'disabled': True}, default=1)
    power = IntegerField('Power', [validators.NumberRange(min=0)], render_kw={'disabled': True}, default=1)
    defense = IntegerField('Defense', [validators.NumberRange(min=0)], render_kw={'disabled': True}, default=1)
    stonks = IntegerField('Stonks', [validators.NumberRange(min=0)], render_kw={'disabled': True}, default=1)
    stocks = FieldList(FormField(StockEntryForm), min_entries=1)
    submit = SubmitField('Save Broker')

    def __init__(self, *args, **kwargs):
        super(BrokerForm, self).__init__(*args, **kwargs)
        
        #self.adjust_stock_entries()

    def adjust_stock_entries(self):
        rarity = self.rarity.data or 1

        while len(self.stocks) < rarity:
            self.stocks.append_entry()
        while len(self.stocks) > rarity:
            self.stocks.pop_entry()


class PurchaseForm(FlaskForm):
    submit = SubmitField("Purchase (50 pts)")


class BrokerSearchForm(FlaskForm):
    name = StringField("Name")
    rarityMin = IntegerField("Rarity (Min.)")
    rarityMax = IntegerField("Rarity (Max.)")
    sort = SelectField("Columns", [validators.Optional()], choices=[])
    order = SelectField("Order", [validators.Optional()], choices=[("asc","+"), ("desc","-")])
    page = IntegerField("page")
    submit = SubmitField("Filter")

class BrokerUpgradeForm(FlaskForm):
    symbol = HiddenField('Symbol', [validators.Length(min=1, max=10)])
    shares = IntegerField('Shares', [validators.NumberRange(min=1)])
    broker_id = HiddenField("broker_id")
    submit = SubmitField("Purchase Shares")

class AssociationSearchForm(FlaskForm):
    username = StringField("Username")
    broker_name = StringField("Broker Name")
    sort = SelectField("Columns", [validators.Optional()], choices=[("username", "username"), ("broker_name","broker name")])
    order = SelectField("Order", [validators.Optional()], choices=[("asc","+"), ("desc","-")])
    # page = IntegerField("page", default=1)
    submit = SubmitField("Filter")