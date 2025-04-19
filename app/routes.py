from app import app
from flask import render_template

@app.route('/')
def index():
    return render_template("index.html")


# ------------------------------------------------------------------
# TODO: Move this to a forms.py file if we end up with more forms

from flask_wtf import FlaskForm
from flask_wtf.file import FileField

from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

import pandas as pd
import io


class UploadForm(FlaskForm):
    file = FileField('Select a File', validators=[ DataRequired() ])
    submit = SubmitField('Submit')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    form = UploadForm()

    # validate_on_submit returns True if the method is POST
    # and the field conforms to all valiadators
    if form.validate_on_submit():
        file_data = io.BytesIO(form.file.data.read())
        df = pd.read_csv(file_data, encoding='utf-8')
        print(df.head())  # Only for debugging and print first few rows.

    return render_template('upload.html', form=form)

# ------------------------------------------------------------------



