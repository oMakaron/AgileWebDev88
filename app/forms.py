from flask_wtf import FlaskForm
from flask_wtf.file import FileField

from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class UploadForm(FlaskForm):
    file = FileField('Select a File', validators=[ DataRequired() ])
    spec = StringField('Specify a format', validators=[ DataRequired() ])
    submit = SubmitField('Submit')

