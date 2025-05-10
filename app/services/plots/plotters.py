from typing import Optional

import matplotlib
# force non-interactive backend before importing pyplot
matplotlib.use('Agg')
from matplotlib.figure import Figure

from pandas import DataFrame

from app.services.plots.registry import PlotRegistry

registry = PlotRegistry(remaps={
    bool: lambda string: string.lower() == 'true',
    tuple[int, int]: lambda string: tuple(int(val.removeprefix('_')) for val in string.split('x')),
})

@registry.register_as('line')
def plot_line(
    source: DataFrame,
    x_col: str, y_col: str,
    title: str = 'Line Plot', x_label: Optional[str] = None, y_label: Optional[str] = None,
    color: str = 'blue', figsize: tuple[int, int] = (10, 6), grid: bool = True
) -> Figure:
    fig = Figure(figsize=figsize)
    ax  = fig.add_subplot(1, 1, 1)
    ax.plot(source[x_col], source[y_col], color=color)
    ax.set(title=title, xlabel=x_label or x_col, ylabel=y_label or y_col)
    ax.grid(visible=grid)
    return fig

@registry.register_as('scatter')
def plot_scatter(
    source: DataFrame,
    x_col: str, y_col: str,
    title: str = 'Scatter Plot', x_label: Optional[str] = None, y_label: Optional[str] = None,
    color: str = 'blue', figsize: tuple[int, int] = (10, 6), grid: bool = True
) -> Figure:
    fig = Figure(figsize=figsize)
    ax  = fig.add_subplot(1, 1, 1)
    ax.scatter(source[x_col], source[y_col], color=color)
    ax.set(title=title, xlabel=x_label or x_col, ylabel=y_label or y_col)
    ax.grid(visible=grid)
    return fig

@registry.register_as('bar')
def plot_bar(
    source: DataFrame,
    x_col: str, y_col: str,
    title: str = 'Bar Chart', x_label: Optional[str] = None, y_label: Optional[str] = None,
    color: str = 'blue', figsize: tuple[int, int] = (10, 6), grid: bool = True
) -> Figure:
    fig = Figure(figsize=figsize)
    ax  = fig.add_subplot(1, 1, 1)
    ax.bar(source[x_col], source[y_col], color=color)
    ax.set(title=title, xlabel=x_label or x_col, ylabel=y_label or y_col)
    ax.grid(visible=grid)
    return fig

@registry.register_as('histogram')
def plot_histogram(
    source: DataFrame,
    column: str, bins: int = 10,
    title: str = 'Histogram', x_label: Optional[str] = None, y_label: Optional[str] = None,
    color: str = 'blue', figsize: tuple[int, int] = (10, 6), grid: bool = True
) -> Figure:
    fig = Figure(figsize=figsize)
    ax  = fig.add_subplot(1, 1, 1)
    ax.hist(source[column], bins=bins, color=color)
    ax.set(title=title, xlabel=x_label or column, ylabel=y_label or 'Frequency')
    ax.grid(visible=grid)
    return fig

@registry.register_as('pie')
def plot_pie(
    source: DataFrame,
    column: str, angle: float = 90,
    title: str = 'Pie Chart', figsize: tuple[int, int] = (10, 6)
) -> Figure:
    fig = Figure(figsize=figsize)
    ax  = fig.add_subplot(1, 1, 1)
    counts = source[column].value_counts()
    ax.pie(
        counts,
        startangle=angle,
        labels=counts.index.to_list(),
        autopct='%1.1f%%'
    )
    ax.set(title=title)
    return fig

@registry.register_as('area')
def plot_area(
    source: DataFrame,
    x_col: str, y_col: str,
    title: str = 'Area Plot', x_label: Optional[str] = None, y_label: Optional[str] = None,
    color: str = 'blue', figsize: tuple[int, int] = (10, 6), grid: bool = True
) -> Figure:
    fig = Figure(figsize=figsize)
    ax  = fig.add_subplot(1, 1, 1)
    ax.stackplot(source[x_col], source[y_col], color=color)
    ax.set(title=title, xlabel=x_label or x_col, ylabel=y_label or y_col)
    ax.grid(visible=grid)
    return fig

@registry.register_as('box')
def plot_box(
    source: DataFrame,
    x_col: str, y_col: str,
    title: str = 'Box Plot', x_label: Optional[str] = None, y_label: Optional[str] = None,
    figsize: tuple[int, int] = (10, 6), grid: bool = True
) -> Figure:
    fig = Figure(figsize=figsize)
    ax  = fig.add_subplot(1, 1, 1)
    source.boxplot(column=y_col, by=x_col, ax=ax)
    ax.set(title=title, xlabel=x_label or x_col, ylabel=y_label or y_col)
    ax.grid(visible=grid)
    return fig
