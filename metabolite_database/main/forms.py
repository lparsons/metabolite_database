from flask_wtf import FlaskForm
from wtforms import SelectField, SelectMultipleField, SubmitField, widgets
from wtforms.validators import DataRequired


class MultiCheckboxField(SelectMultipleField):
    """
    A multiple-select, except displays a list of checkboxes.

    Iterating the field will produce subfields, allowing custom rendering of
    the enclosed checkbox fields.
    """
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class RetentionTimesForm(FlaskForm):
    compoundlist = SelectField('Compound List', validators=[DataRequired()])
    standardruns = MultiCheckboxField(
        'Standard Runs', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Get List')
    export = SubmitField('Export as CSV')
