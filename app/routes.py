from app import app
from flask import render_template

@app.route('/')
def index():
    return render_template("index.html")


from flask_wtf import FlaskForm

from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class TestForm(FlaskForm):
    string = StringField('Enter Some Words', validators=[DataRequired()])
    submit = SubmitField('Submit')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    form = TestForm()

    # validate_on_submit returns True if the method is POST
    # and the field conforms to all valiadators
    if form.validate_on_submit():
        print(form.string.data)

    return render_template('upload.html', form=form)
