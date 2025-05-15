from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms.widgets import ColorInput
from wtforms import (
    StringField, SelectField,
    SubmitField, PasswordField
)
from wtforms.validators import (
    DataRequired, Email, EqualTo,
    Length, Optional
)

class UploadForm(FlaskForm):
    file = FileField(
        'Select a File',
        validators=[
            FileRequired("You must upload a CSV."),
            FileAllowed(['csv'], "Please select a CSV file.")
        ]
    )
    submit_upload = SubmitField('Upload File')


class ChartForm(FlaskForm):
    # turn *off* CSRF for this secondary form
    class Meta:
        csrf = False

    graph_type = SelectField(
        'Graph Type',
        choices=[('', '– Select a chart –'),
                 ('line', 'Line'),
                 ('bar', 'Bar'),
                 ('scatter', 'Scatter'),
                 ('area', 'Area'),
                 ('box', 'Box'),
                 ('histogram', 'Histogram'),
                 ('pie', 'Pie')],
        validators=[DataRequired()]
    )

    # always include a blank first choice so it starts empty
    x_col = SelectField('X Axis', choices=[('', '– Select X –')], validate_choice=False)
    y_col = SelectField('Y Axis', choices=[('', '– Select Y –')], validate_choice=False)
    column = SelectField('Column', choices=[('', '– Select column –')], validate_choice=False)

    # Optional Common Fields
    title   = StringField('Title',           validators=[Optional()])
    x_label = StringField('X Axis Label',   validators=[Optional()])
    y_label = StringField('Y Axis Label',   validators=[Optional()])
    color   = StringField('Color', widget=ColorInput(), default="#0000ff", validators=[Optional()])
    figsize = StringField('Figure Size (e.g. 10x6)', validators=[Optional()])
    grid    = SelectField(
        'Show Grid',
        choices=[('true','Yes'),('false','No')],
        validators=[Optional()]
    )

    # Histogram-specific
    bins        = StringField('Bins',            validators=[Optional()])
    density     = SelectField('Density', choices=[('true','Yes'),('false','No')], validators=[Optional()])
    cumulative  = SelectField('Cumulative', choices=[('true','Yes'),('false','No')], validators=[Optional()])
    orientation = SelectField('Orientation', choices=[('vertical','Vertical'),('horizontal','Horizontal')], validators=[Optional()])
    histtype    = SelectField('Hist Type', choices=[('bar','Bar'),('barstacked','Stacked'),('step','Step'),('stepfilled','Step Filled')], validators=[Optional()])
    alpha       = StringField('Alpha',          validators=[Optional()])

    # Pie-specific
    angle        = StringField('Start Angle',  validators=[Optional()])
    explode      = StringField('Explode (comma-separated)', validators=[Optional()])
    autopct      = StringField('AutoPct Format (e.g. %1.1f%%)', validators=[Optional()])
    shadow       = SelectField('Shadow', choices=[('true','Yes'),('false','No')], validators=[Optional()])
    radius       = StringField('Radius',       validators=[Optional()])
    pctdistance  = StringField('Pct Distance', validators=[Optional()])
    labeldistance= StringField('Label Distance', validators=[Optional()])
    colors       = StringField('Slice Colors (comma-separated)', validators=[Optional()])

    # Scatter-specific
    marker = StringField('Marker',      validators=[Optional()])
    size   = StringField('Point Size',  validators=[Optional()])

    # Area-specific
    labels   = StringField('Labels (comma-separated)', validators=[Optional()])
    baseline = StringField('Baseline',   validators=[Optional()])

    # Box-specific
    notch        = SelectField('Notch', choices=[('true','Yes'),('false','No')], validators=[Optional()])
    vert         = SelectField('Vertical', choices=[('true','Yes'),('false','No')], validators=[Optional()])
    patch_artist = SelectField('Patch Artist', choices=[('true','Yes'),('false','No')], validators=[Optional()])
    showfliers   = SelectField('Show Fliers', choices=[('true','Yes'),('false','No')], validators=[Optional()])

    # Bar-specific
    width = StringField('Bar Width', validators=[Optional()])
    align = SelectField('Align', choices=[('center','Center'),('edge','Edge')], validators=[Optional()])

    submit_generate = SubmitField('Generate Chart')
    submit_save = SubmitField('Save Chart')



class SignupForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=8, message='Password too short. Minimum 8 characters.')
    ])
    confirm = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match.')
    ])
    submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')

class EditProfileForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('New Password (optional)', validators=[Optional()])
    submit = SubmitField('Save Changes')
