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


class UploadForm(FlaskForm):
    file = FileField('Select a File', validators=[ DataRequired() ])
    submit = SubmitField('Submit')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    form = UploadForm()

    # validate_on_submit returns True if the method is POST
    # and the field conforms to all valiadators
    if form.validate_on_submit():
        data = form.file.data.read().decode('utf-8').strip()

        # here is where we hand off to the csv parser / graph renderer, but
        # for now we will just print to the console to demonstate it works
        print(data)

    return render_template('upload.html', form=form)

# ------------------------------------------------------------------

