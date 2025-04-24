from app import app
from app.forms import UploadForm

from io import BytesIO
from flask import render_template

from app.logic.plotter import plot_frame, read_csv, save_to_string
from app.logic.specifier import Specifier

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template("login.html")


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    form = UploadForm()
    chart = None

    # returns True if the method is POST and the field conforms to all valiadators
    if form.validate_on_submit():

        # parses primitive frame data into useful constructs
        data = read_csv(BytesIO(form.file.data.read()))
        spec = Specifier.from_string(form.spec.data)

        # generates a base64 encoding of a png so that we don't have to save locally
        figure = plot_frame(data, spec)
        image = save_to_string(figure)

        # this boilerplate is necessary to get the browser to interpret the string as a png
        chart = f"data:image/png;base64,{image}"

    return render_template('upload.html', form=form, chart=chart)

