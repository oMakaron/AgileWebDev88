from app import app
from app.forms import UploadForm

from io import BytesIO
from flask import render_template

from app.logic.plotter import read_csv, save_to_string

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template("login.html")

@app.route('/dashboard')
def dashboard():
    return render_template("dashboard.html")

# ------------------------------------------------------------------
# TODO: Move this to a forms.py file if we end up with more forms

from flask_wtf import FlaskForm
from flask_wtf.file import FileField

from wtforms import SubmitField
from wtforms.validators import DataRequired

import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot
from pandas.core.generic import is_numeric_dtype

from os import path


class UploadForm(FlaskForm):
    file = FileField('Select a File', validators=[ DataRequired() ])
    submit = SubmitField('Submit')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    form = UploadForm()
    path_chart = None #path for fronted

    # validate_on_submit returns True if the method is POST
    # and the field conforms to all valiadators
    if form.validate_on_submit():
        user_file = BytesIO(form.file.data.read())
        df = read_csv(user_file)

        #a really basic way to generating image
        x_col = None
        y_col = None

        for col in df.columns:
            if df[col].dtype == 'object':
                x_col = col
                break

        for col in df.columns:
            if is_numeric_dtype(df[col]):
                y_col = col
                if col != x_col:
                    break


        if x_col and y_col:
            matplotlib.pyplot.figure(figsize=(4, 2))  # chart size we can change later
            df.plot(x=x_col, y=y_col, kind='bar', legend=False) # we can change type bar to the others, just for now
            matplotlib.pyplot.tight_layout()

            path_static = path.join(app.root_path, 'static', 'chart.png')
            matplotlib.pyplot.savefig(path_static)
            matplotlib.pyplot.close()

            path_chart = 'chart.png'

    return render_template('upload.html', form=form, chart=path_chart)

# ------------------------------------------------------------------

