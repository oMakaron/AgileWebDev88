import pandas as pd
import matplotlib.pyplot as plt
import io

def plot_line(x_col, y_col, title='Line Plot', color='blue', xlabel=None, ylabel=None, figsize=(10, 6), grid=True):
    df = pd.read_csv("dataFrame.csv")

    # Create a line plot
    ax = df.plot(x=x_col, y=y_col, kind='line', color=color, title=title, figsize=figsize)
    ax.set_xlabel(xlabel if xlabel else x_col)
    ax.set_ylabel(ylabel if ylabel else y_col)
    if grid:
        plt.grid()
    #plt.show

    # Save to PNG in a memory buffer 
    img_buf = io.BytesIO()
    plt.savefig(img_buf, format='png')
    img_buf.seek(0)
    return img_buf

def plot_scatter(x_col, y_col, title='Scatter Plot', color='blue', xlabel=None, ylabel=None, figsize=(10, 6), grid=True):
    df = pd.read_csv("dataFrame.csv")

    # Create a scatter plot
    ax = df.plot(x=x_col, y=y_col, kind='scatter', color=color, title=title, figsize=figsize)
    ax.set_xlabel(xlabel if xlabel else x_col)
    ax.set_ylabel(ylabel if ylabel else y_col)
    if grid:
        plt.grid()
    #plt.show()

    # Save to PNG in a memory buffer 
    img_buf = io.BytesIO()
    plt.savefig(img_buf, format='png')
    img_buf.seek(0)
    return img_buf

def plot_bar(x_col, y_col, title='Bar Chart', color='blue', xlabel=None, ylabel=None, figsize=(10, 6), grid=True):
    df = pd.read_csv("dataFrame.csv")

    # Create a bar chart
    ax = df.plot(x=x_col, y=y_col, kind='bar', color=color, title=title, figsize=figsize)
    ax.set_xlabel(xlabel if xlabel else x_col)
    ax.set_ylabel(ylabel if ylabel else y_col)
    if grid:
        plt.grid()
    #plt.show()

    # Save to PNG in a memory buffer 
    img_buf = io.BytesIO()
    plt.savefig(img_buf, format='png')
    img_buf.seek(0)
    return img_buf

def plot_histogram(column, title='Histogram', color='blue', bins=10, xlabel=None, ylabel='Frequency', figsize=(10, 6), grid=True):
    df = pd.read_csv("dataFrame.csv")

    #Create a histogram
    ax = df[column].plot(kind='hist', color=color, title=title, bins=bins, figsize=figsize)
    ax.set_xlabel(xlabel if xlabel else column)
    ax.set_ylabel(ylabel)
    if grid:
        plt.grid()
    #plt.show()

    # Save to PNG in a memory buffer 
    img_buf = io.BytesIO()
    plt.savefig(img_buf, format='png')
    img_buf.seek(0)
    return img_buf

def plot_pie(column, title='Pie Chart', figsize=(8, 8), angle = 90):
    df = pd.read_csv("dataFrame.csv")

    # Create a pie chart
    plt.figure(figsize=figsize)
    df[column].value_counts().plot(kind='pie', title=title, autopct='%1.1f%%', startangle=angle)
    plt.ylabel('')  # Hide the y-label
    #plt.show()

    # Save to PNG in a memory buffer 
    img_buf = io.BytesIO()
    plt.savefig(img_buf, format='png')
    img_buf.seek(0)
    return img_buf

def plot_area(x_col, y_col, title='Area Plot', color='blue', xlabel=None, ylabel=None, figsize=(10, 6), grid=True):
    df = pd.read_csv("dataFrame.csv")

    # Create an area plot
    ax = df.plot(x=x_col, y=y_col, kind='area', color=color, title=title, figsize=figsize)
    ax.set_xlabel(xlabel if xlabel else x_col)
    ax.set_ylabel(ylabel if ylabel else y_col)
    if grid:
        plt.grid()
    #plt.show()

    # Save to PNG in a memory buffer 
    img_buf = io.BytesIO()
    plt.savefig(img_buf, format='png')
    img_buf.seek(0)
    return img_buf

def plot_box(x_col, y_col, title='Box Plot', xlabel=None, ylabel=None, figsize=(10, 6), grid=True):
    df = pd.read_csv("dataFrame.csv")

    # Create a box plot
    ax = df.boxplot(column=y_col, by=x_col, grid=grid, figsize=figsize)
    plt.title(title)
    plt.xlabel(xlabel if xlabel else x_col)
    plt.ylabel(ylabel if ylabel else y_col)
    if grid:
        plt.grid()
    #plt.show()

    # Save to PNG in a memory buffer 
    img_buf = io.BytesIO()
    plt.savefig(img_buf, format='png')
    img_buf.seek(0)
    return img_buf