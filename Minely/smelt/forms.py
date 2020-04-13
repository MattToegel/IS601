from markupsafe import escape
from flask_wtf import FlaskForm
from wtforms import SelectField, IntegerField, SubmitField, validators


def coerce_for_enum(enum):
    def coerce(name):
        if isinstance(name, enum):
            return name.value
        try:
            return enum[name]
        except KeyError:
            raise ValueError(name)

    return coerce


class SmelterForm(FlaskForm):
    options = SelectField('Item', [validators.Optional()],
                          render_kw={'class': 'custom-select', 'style': 'height:auto;'})
    quantity = IntegerField('Quantity', render_kw={'class': 'form-control', 'type': 'number', 'max': '50', 'min': '1'})
    submit = SubmitField('Add', render_kw={'class': 'form-control btn btn-primary'})

    def set_options(self, choices):
        self.options.choices = choices
