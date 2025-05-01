from werkzeug.wrappers import response
from app import app
from flask import Response, render_template, jsonify

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
# Source endpoints

@app.route('/sources', methods=['GET'])
def get_available_sources() -> Response:
    response = jsonify({
        'sources': [{'name': 'File Name 1', 'file_id': 10},
                    {'name': 'File Name 2', 'file_id': 11}]
    })

    response.status_code = 200
    return response

@app.route('/sources', methods=['POST'])
def make_new_source() -> Response:
    response = jsonify({'file_id': 12})
    response.status_code = 201
    return response

@app.route('/sources/<file_id:int>', methods=['GET'])
def get_source(file_id: int) -> Response:
    response = jsonify({'file_id': file_id, 'content': 'h1,h2,h3\n1,2,3'})
    response.status_code = 200
    return response

@app.route('/sources/<file_id:int>', methods=['PUT'])
def update_source(file_id: int) -> Response:
    response = jsonify({'file_id': file_id})
    response.status_code = 200
    return response

@app.route('/sources/<file_id:int>', methods=['DELETE'])
def delete_source(file_id: int) -> Response:
    response = jsonify({'message': 'File deleted successfully'})
    response.status_code = 200
    return response

# ------------------------------------------------------------------
# Chart endpoints

@app.route('/charts', methods=['GET'])
def get_available_charts() -> Response:
    response = jsonify({
        'charts': [{'name': 'Chart 1', 'chart_id': 10},
                   {'name': 'Chart 2', 'chart_id': 11}]
    })
    response.status_code = 200
    return response

@app.route('/charts', methods=['POST'])
def make_new_chart() -> Response:
    response = jsonify({'chart_id': 12})
    response.status_code = 201
    return response

@app.route('/charts/<chart_id:int>', methods=['GET'])
def get_chart(chart_id: int) -> Response:
    response = jsonify({'chart_id': chart_id, 'file_id': 11, 'spec': 'type=line'})
    response.status_code = 200
    return response

@app.route('/charts/<chart_id:int>', methods=['PUT'])
def update_chart(chart_id: int) -> Response:
    response = jsonify({'chart_id': chart_id})
    response.status_code = 200
    return response

@app.route('/charts/<chart_id:int>', methods=['DELETE'])
def delete_chart(chart_id: int) -> Response:
    response = jsonify({'message': 'Chart deleted successfully.'})
    response.status_code = 200
    return response

@app.route('/chart/<chart_id:int>/view', methods=['GET'])
def get_chart_view(chart_id: int) -> Response:
    response = jsonify({'name': 'Chart Name', 'chart_id': chart_id, 'content': 'chart.png'})
    response.status_code = 200
    return response

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

import plots
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
