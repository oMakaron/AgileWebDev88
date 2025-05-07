from typing import Optional

from matplotlib.figure import Figure
from matplotlib.pyplot import subplots

from pandas import DataFrame

from app.services.plots.registry import PlotRegistry


registry = PlotRegistry(remaps={
    # makes it so that match 'true' are true and everything else is false.
    # TODO: Make this explicitly check for false and throw an error if neither true not false
    bool: lambda string: string.lower() == 'true',

    # TODO: Allow tuples in the parser, or at the very least allow values to start with numbers so
    # the `_` prefix is not necesary
    tuple[int, int]: lambda string: tuple(int(val.removeprefix('_')) for val in string.split('x')),
})


@registry.register_as('line')
def plot_line(
    source: DataFrame,
    x_col: str, y_col: str,
    title: str = 'Line Plot', x_label: Optional[str] = None, y_label: Optional[str] = None,
    color: str = 'blue', figsize: tuple[int, int] = (10, 6), grid: bool = True
) -> Figure:

    # Create a line graph
    figure, axes = subplots(figsize=figsize)
    axes.plot(source[x_col], source[y_col], color = color)
    axes.set(title = title, xlabel = x_label or x_col, ylabel = y_label or y_col)
    axes.grid(visible=grid)

    return figure


@registry.register_as('scatter')
def plot_scatter(
    source: DataFrame,
    x_col: str, y_col: str,
    title: str = 'Scatter Plot', x_label: Optional[str] = None, y_label: Optional[str] = None,
    color: str = 'blue', figsize: tuple[int, int] = (10, 6), grid: bool = True
) -> Figure:

    # Create a scatter plot
    figure, axes = subplots(figsize=figsize)
    axes.scatter(source[x_col], source[y_col], color = color)
    axes.set(title = title, xlabel = x_label or x_col, ylabel = y_label or y_col)
    axes.grid(visible=grid)

    return figure


@registry.register_as('bar')
def plot_bar(
    source: DataFrame,
    x_col: str, y_col: str,
    title: str = 'Bar Chart', x_label: Optional[str] = None, y_label: Optional[str] = None,
    color:str = 'blue', figsize: tuple[int, int] = (10, 6), grid: bool = True
) -> Figure:

    # Create a bar chart
    figure, axes = subplots(figsize=figsize)
    axes.bar(source[x_col], source[y_col], color = color)
    axes.set(title = title, xlabel = x_label or x_col, ylabel = y_label or y_col)
    axes.grid(visible=grid)

    return figure


@registry.register_as('histogram')
def plot_histogram(
    source: DataFrame,
    column: str, bins: int = 10,
    title: str = 'Histogram', x_label: Optional[str] = None, y_label: Optional[str] = None,
    color: str = 'blue', figsize: tuple[int, int] = (10, 6), grid: bool = True
) -> Figure:

    # Create a histogram
    figure, axes = subplots(figsize=figsize)
    axes.hist(source[column], bins = bins, color = color)
    axes.set(title = title, xlabel = x_label or column, ylabel = y_label or 'Frequency')
    axes.grid(visible=grid)

    return figure


@registry.register_as('pie')
def plot_pie(
    source: DataFrame,
    column: str, angle: float = 90,
    title: str = 'Pie Chart', figsize: tuple[int, int] = (10, 6)
) -> Figure:

    # Create a pie chart
    figure, axes = subplots(figsize = figsize)
    counts = source[column].value_counts()
    axes.pie(counts, startangle = angle, labels = counts.index.to_list(), autopct = '%1.1f%%')
    axes.set(title = title)

    return figure


@registry.register_as('area')
def plot_area(
    source: DataFrame,
    x_col: str, y_col: str,
    title: str = 'Area Plot', x_label: Optional[str] = None, y_label: Optional[str] = None,
    color: str = 'blue', figsize: tuple[int, int] = (10, 6), grid: bool = True
) -> Figure:

    # Create an area plot
    figure, axes = subplots(figsize = figsize)
    axes.stackplot(source[x_col], source[y_col], color = color)
    axes.set(title = title, xlabel = x_label or x_col, ylabel = y_label or y_col)
    axes.grid(visible=grid)

    return figure


@registry.register_as('box')
def plot_box(
    source: DataFrame,
    x_col: str, y_col: str,
    title: str = 'Box Plot', x_label: Optional[str] = None, y_label: Optional[str] = None,
    figsize: tuple[int, int] = (10, 6), grid: bool = True
) -> Figure:

    # Create a box plot
    figure, axes = subplots(figsize = figsize)
    source.boxplot(column = y_col, by = x_col, ax = axes)

    axes.set(title = title, xlabel = x_label or x_col, ylabel = y_label or y_col)
    axes.grid(visible=grid)

    return figure

