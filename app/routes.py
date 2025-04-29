from app import app
from flask import render_template, request, redirect

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template("login.html")

@app.route('/dashboard')
def dashboard():
    return render_template("dashboard.html")

@app.route('/friends', methods=['GET'])
def friends():
    return render_template("friends.html")

@app.route('/add-friend', methods=['GET', 'POST'])
def add_friend():
    if request.method == 'POST':
        # Handle form submission (e.g., save friend data)
        friend_name = request.form.get('friend_name')
        friend_email = request.form.get('friend_email')
        # Save the data (this is just a placeholder, implement actual logic)
        print(f"Added Friend: {friend_name}, Email: {friend_email}")
        return redirect('/friends')  # Redirect back to the friends page after saving

    return render_template("add_friend.html")

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

@app.route('/upload', methods=['GET', 'POST'])
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

# ------------------------------------------------------------------

from app import plots
from flask import send_file, request

# plot endpoints
@app.route('/plot/line')
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
def plotPie():
    col = request.args.get('col')                            
    title = request.args.get('title', default= 'Histogram Plot') 
    fig = request.args.get('fig', default= '8,8').split(',')   # format num,num
    fig = (int(fig[0]), int(fig[1]))
    angle = request.args.get('angle', type= int, default= 90)

    plotData = plots.plot_pie(column= col, title= title, figsize= fig, angle= angle)
    return send_file(plotData, mimetype='image/png')

@app.route('/plot/area')
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
