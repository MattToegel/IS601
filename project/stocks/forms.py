from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, validators, SubmitField

class StockSearchForm(FlaskForm):
    symbol = StringField('Symbol', [validators.Length(min=1, max=10)])
    submit = SubmitField("Find")
class StockForm(FlaskForm):
    symbol = StringField('Symbol', [validators.Length(min=1, max=10)])
    open = DecimalField('Open', [validators.NumberRange(min=0)])
    high = DecimalField('High', [validators.NumberRange(min=0)])
    low = DecimalField('Low', [validators.NumberRange(min=0)])
    price = DecimalField('Price', [validators.NumberRange(min=0)])
    volume = DecimalField('Volume', [validators.NumberRange(min=0)])
    latest_trading_day = StringField('Latest Trading Day (YYYY-MM-DD)', [validators.Regexp(r'^\d{4}-\d{2}-\d{2}$', message="Invalid date format")])
    previous_close = DecimalField('Previous Close', [validators.NumberRange(min=0)])
    change = DecimalField('Change', [validators.NumberRange(min=0)])
    change_percent = DecimalField('Change Percent', [validators.NumberRange(min=0)])
    submit = SubmitField("Save")
