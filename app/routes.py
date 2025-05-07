from app import app
from flask import render_template, request, redirect, url_for, flash, session
from app.model import User
from app.model import db
from app.form import SignupForm, LoginForm
from functools import wraps

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('You need to log in to access this page.')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Logout successful!', 'success')
    return redirect(url_for('login'))


@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            session['user_id'] = user.id
            flash('Login successful!', 'success')  # Flash success message
            return redirect('/dashboard')  # Redirect to the dashboard
        flash('Invalid email or password.', 'error')  # Flash error message

    return render_template('login.html', form=form)

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template("dashboard.html")

@app.route('/edit-profile', methods=['GET', 'PATCH'])
@login_required
def edit_profile():
    if request.method == 'PATCH':
        # Handle form submission (e.g., save updated profile data)
        name = request.form.get('name')
        email = request.form.get('email')
        # Save the data (this is just a placeholder, implement actual logic)
        print(f"Updated Name: {name}, Updated Email: {email}")
        return redirect('/profile')  # Redirect back to the profile page after saving

    return render_template("edit_profile.html")


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('Email already registered.')
            return redirect('/signup')

        new_user = User(
            fullname=form.name.data,
            email=form.email.data
        )
        new_user.set_password(form.password.data)

        db.session.add(new_user)
        db.session.commit()
        flash('Signup successful!')
        return redirect('/login')

    return render_template('signup.html', form=form)



@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    return render_template('settings.html')

@app.route('/friends', methods=['GET'])
@login_required
def friends():
    return render_template('friends.html')

@app.route('/analytics')
@login_required
def analytics():
    return render_template('analytics.html')

@app.route('/profile')
@login_required
def profile():
    user = User.query.get(session['user_id'])
    return render_template('profile.html', user=user)

@app.route('/add-friend', methods=['GET', 'POST'])
@login_required
def add_friend():
    return render_template('add_friend.html')

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    form = UploadForm()
    path_chart = None #path for fronted

    # validate_on_submit returns True if the method is POST
    # and the field conforms to all valiadators
    if form.validate_on_submit():
        user_file = io.BytesIO(form.file.data.read())
        df = pandas.read_csv(user_file, encoding='utf-8')
        df.to_csv("dataFrame.csv", index= False) # For importing purposes, would be better to use database

        #a really basic way to generating image
        x_col = None
        y_col = None

        for col in df.columns:
            if df[col].dtype == 'object':
                x_col = col
                break

        for col in df.columns:
            if pandas.api.types.is_numeric_dtype(df[col]):
                y_col = col
                if col != x_col:
                    break


        if x_col and y_col:
            matplotlib.pyplot.figure(figsize=(4, 2))  # chart size we can change later
            df.plot(x=x_col, y=y_col, kind='bar', legend=False) # we can change type bar to the others, just for now
            matplotlib.pyplot.tight_layout()

            path_static = os.path.join(app.root_path, 'static', 'chart.png')
            matplotlib.pyplot.savefig(path_static)
            matplotlib.pyplot.close()

            path_chart = 'chart.png'

    return render_template('upload.html', form=form, chart=path_chart)


@app.route('/visualise', methods=['GET', 'POST'])
@login_required
def visualise():
    chart = None
    if request.method == 'GET':
        # Handle visualization logic here
        x_col = request.args.get('xCol')
        y_col = request.args.get('yCol')
        chart_type = request.args.get('chartType')
        title = request.args.get('title', 'Visualization')
        color = request.args.get('color', 'blue')
        grid = request.args.get('grid', '1') == '1'
        figsize = tuple(map(int, request.args.get('figsize', '10,6').split(',')))

        # Generate the chart using your existing plotting functions
        if x_col and y_col and chart_type:
            if chart_type == 'line':
                chart = plots.plot_line(x_col, y_col, title=title, color=color, grid=grid, figsize=figsize)
            elif chart_type == 'bar':
                chart = plots.plot_bar(x_col, y_col, title=title, color=color, grid=grid, figsize=figsize)
            # Add other chart types here...

    return render_template('visualise.html', chart=chart)

# ------------------------------------------------------------------
# TODO: Move this to a forms.py file if we end up with more forms

from flask_wtf import FlaskForm
from flask_wtf.file import FileField

from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

import pandas
import io

import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot

import os


class UploadForm(FlaskForm):
    file = FileField('Select a File', validators=[ DataRequired() ])
    submit = SubmitField('Submit')

# ------------------------------------------------------------------

from app import plots
from flask import send_file, request

# plot endpoints
@app.route('/plot/line')
@login_required
def plotLine():
    x = request.args.get('xCol')                            
    y = request.args.get('yCol').split(',') # format str,str,...
    title = request.args.get('title', default= 'Line Plot') 
    color = request.args.get('color', default= 'blue')
    xlabel = request.args.get('xlabel')
    ylabel = request.args.get('ylabel')
    fig = request.args.get('fig', default= '10,6').split(',')   # format num,num
    fig = (int(fig[0]), int(fig[1]))
    grid = request.args.get('grid', type= int)
    grid = True if grid == 1 else False

    plotData = plots.plot_line(x_col= x, y_col= y, title= title, color= color, xlabel= xlabel, ylabel= ylabel, figsize= fig, grid= grid)
    return send_file(plotData, mimetype='image/png')

@app.route('/plot/scatter')
@login_required
def plotScat():
    x = request.args.get('xCol')                            
    y = request.args.get('yCol').split(',') # format str,str,...
    title = request.args.get('title', default= 'Scatter Plot') 
    color = request.args.get('color', default= 'blue')
    xlabel = request.args.get('xlabel')
    ylabel = request.args.get('ylabel')
    fig = request.args.get('fig', default= '10,6').split(',')   # format num,num
    fig = (int(fig[0]), int(fig[1]))
    grid = request.args.get('grid', type= int)
    grid = True if grid == 1 else False

    plotData = plots.plot_scatter(x_col= x, y_col= y, title= title, color= color, xlabel= xlabel, ylabel= ylabel, figsize= fig, grid= grid)
    return send_file(plotData, mimetype='image/png')

@app.route('/plot/bar')
@login_required
def plotBar():
    x = request.args.get('xCol')                            
    y = request.args.get('yCol').split(',') # format str,str,...
    title = request.args.get('title', default= 'Bar Plot') 
    color = request.args.get('color', default= 'blue')
    xlabel = request.args.get('xlabel')
    ylabel = request.args.get('ylabel')
    fig = request.args.get('fig', default= '10,6').split(',')   # format num,num
    fig = (int(fig[0]), int(fig[1]))
    grid = request.args.get('grid', type= int)
    grid = True if grid == 1 else False

    plotData = plots.plot_bar(x_col= x, y_col= y, title= title, color= color, xlabel= xlabel, ylabel= ylabel, figsize= fig, grid= grid)
    return send_file(plotData, mimetype='image/png')

@app.route('/plot/histogram')
@login_required
def plotHist():
    col = request.args.get('col')                            
    title = request.args.get('title', default= 'Pie Chart') 
    color = request.args.get('color', default= 'blue')
    xlabel = request.args.get('xlabel')
    ylabel = request.args.get('ylabel', default= 'Frequency')
    fig = request.args.get('fig', default= '10,6').split(',')   # format num,num
    fig = (int(fig[0]), int(fig[1]))
    grid = request.args.get('grid', type= int)
    grid = True if grid == 1 else False
    bin = request.args.get('bins', type= int)

    plotData = plots.plot_histogram(column= col, title= title, color= color, xlabel= xlabel, ylabel= ylabel, figsize= fig, grid= grid, bins= bin)
    return send_file(plotData, mimetype='image/png')

@app.route('/plot/pie')
@login_required
def plotPie():
    col = request.args.get('col')                            
    title = request.args.get('title', default= 'Histogram Plot') 
    fig = request.args.get('fig', default= '8,8').split(',')   # format num,num
    fig = (int(fig[0]), int(fig[1]))
    angle = request.args.get('angle', type= int, default= 90)

    plotData = plots.plot_pie(column= col, title= title, figsize= fig, angle= angle)
    return send_file(plotData, mimetype='image/png')

@app.route('/plot/area')
@login_required
def plotArea():
    x = request.args.get('xCol')                            
    y = request.args.get('yCol').split(',') # format str,str,...
    title = request.args.get('title', default= 'Area Plot') 
    color = request.args.get('color', default= 'blue')
    xlabel = request.args.get('xlabel')
    ylabel = request.args.get('ylabel')
    fig = request.args.get('fig', default= '10,6').split(',')   # format num,num
    fig = (int(fig[0]), int(fig[1]))
    grid = request.args.get('grid', type= int)
    grid = True if grid == 1 else False

    plotData = plots.plot_area(x_col= x, y_col= y, title= title, color= color, xlabel= xlabel, ylabel= ylabel, figsize= fig, grid= grid)
    return send_file(plotData, mimetype='image/png')

@app.route('/plot/box')
@login_required
def plotBox():
    x = request.args.get('xCol')                            
    y = request.args.get('yCol').split(',') # format str,str,...
    title = request.args.get('title', default= 'Box Plot') 
    xlabel = request.args.get('xlabel')
    ylabel = request.args.get('ylabel')
    fig = request.args.get('fig', default= '10,6').split(',')   # format num,num
    fig = (int(fig[0]), int(fig[1]))
    grid = request.args.get('grid', type= int)
    grid = True if grid == 1 else False

    plotData = plots.plot_box(x_col= x, y_col= y, title= title, xlabel= xlabel, ylabel= ylabel, figsize= fig, grid= grid)
    return send_file(plotData, mimetype='image/png')

# ------------------------------------------------------------------

