from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length

class settings_values(FlaskForm):
    fuel_type = None
    refuel_amount = StringField('Refuel_amount', validators=[DataRequired()])
    fuel_consumption = StringField('Fuel_consumption', validators=[DataRequired()])
    localization = StringField('Localization', validators=[DataRequired()])
    submit = SubmitField('Submit')