from app import app
from app.forms import UploadForm

from io import BytesIO
from flask import render_template


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

import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot

from app.logic.specifier import Parser
from app.logic.plotter import read_csv, save_to_string
from app.plots import registry


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    form = UploadForm()
    chart = None

    # returns True if the method is POST and the field conforms to all valiadators
    if form.validate_on_submit():

        # parses primitive frame data into useful constructs
        data = read_csv(BytesIO(form.file.data.read()))
        spec = Parser.parse_string(form.spec.data)

        if 'type' not in spec:
            raise Exception('Need a type')

        plot_type = spec.pop('type')
        plot_type = plot_type[0] if isinstance(plot_type, list) else plot_type

        plotter = registry.functions[plot_type]

        bound, unbound = plotter.bind_args(source = data, **spec)
        print(bound)
        if unbound:
            print(unbound)

        # generates a base64 encoding of a png so that we don't have to save locally
        figure = plotter.function(**bound)
        image = save_to_string(figure)

        # this boilerplate is necessary to get the browser to interpret the string as a png
        chart = f"data:image/png;base64,{image}"

    return render_template('upload.html', form=form, chart=chart)

# ------------------------------------------------------------------

