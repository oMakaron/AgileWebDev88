from typing import Any, Callable, Optional
from inspect import Parameter, signature

from matplotlib.figure import Figure

import pandas as pd
import matplotlib.pyplot as plt


def unbound_error(param_name: str, f_name: str) -> str:
    return f"Couldn't find parameter {param_name!r} in {f_name}"


class BindError(Exception):

    def __init__(self, missing: list[str], errors: list[tuple[str, Any]], unbound: list[str], func_name: str) -> None:
        self._missing, self._errors, self._unbound = missing, errors, unbound
        self._name = func_name

    def missing(self) -> list[str]:
        return [f"{self._name} requires parameter {name}" for name in self._missing]

    def errors(self) -> list[str]:
        return [f"Cannot convert {value!r} for use as {param!r} in {self._name}" for value, param in self._errors]

    def unbound(self) -> list[str]:
        return [name for name in self._unbound]


class PlotterFunction:
    function: Callable[..., Figure]
    required: list[str] # parameters that don't have a default value will be required
    optional: list[str] # parameters that do have a default value will be optional
    combined: list[str] # contains the total list of parameter names
    annotations: dict[str, Callable] # maps between parameter name and type

    def __init__(self, function: Callable[..., Figure], remaps: dict[Callable, Callable]) -> None:
        sig = signature(function)

        self.function = function
        self.required, self.optional, self.combined  = [], [], []
        self.annotations = dict()

        for name, param in sig.parameters.items():
            self.combined.append(name)
            self.annotations[name] = remaps.get(param.annotation, param.annotation)
            if param.default is Parameter.empty:
                self.required.append(name)
            else:
                self.optional.append(name)

    def bind_args(self, **kwargs) -> tuple[dict[str, Any], list[str]]:
        # finds any args that should be present but are not
        missing = [arg for arg in self.required if not arg in kwargs]

        # attempts to cast arguments to the appropriate type and makes note of errors
        errors = []
        bound = {name: self._cast(name, value, errors) for name, value in kwargs.items() if name in self.combined}

        # makes note of any arguments that are present but unexpected
        unbound = [unbound_error(arg, self.function.__name__) for arg in kwargs.keys() if arg not in self.combined]

        # missing arguments or failed conversions will raise an error
        if missing or errors:
            raise BindError(missing, errors, unbound, self.function.__name__)

        return bound, unbound

    def _cast(self, name: str, value: Any, errors: list) -> Any:
        try:
            return self.annotations[name](value)
        except (TypeError, ValueError):
            errors.append((value, name))
            return None


class PlotRegistry:
    functions: dict[str, PlotterFunction]
    _remaps: dict[Any, Callable]

    def __init__(self, remaps: dict[Any, Callable] | None = None) -> None:
        self.functions = dict()
        self._remaps = remaps or dict()

    def register_as(self, name: str) -> Callable:
        def register(function: Callable) -> Callable:
            self.functions[name] = PlotterFunction(function, self._remaps)
            return function
        return register


registry = PlotRegistry(remaps={
    # makes it so that match 'true' are true and everythin else is false
    bool: lambda string: string.lower() == 'true',

    # TODO: Allow tuples in the parser, or at the very least allow values to start with numbers so
    # the `_` prefix is not necesary
    tuple[int, int]: lambda string: tuple(int(val.removeprefix('_')) for val in string.split('x')),
})


@registry.register_as('line')
def plot_line(
    source: pd.DataFrame,
    x_col: str, y_col: str,
    title: str = 'Line Plot', x_label: Optional[str] = None, y_label: Optional[str] = None,
    color: str = 'blue', figsize: tuple[int, int] = (10, 6), grid: bool = True
) -> Figure:

    # Create a line graph
    figure, axes = plt.subplots(figsize=figsize)
    axes.plot(source[x_col], source[y_col], color = color)
    axes.set(title = title, xlabel = x_label or x_col, ylabel = y_label or y_col)
    axes.grid(visible=grid)

    return figure


@registry.register_as('scatter')
def plot_scatter(
    source: pd.DataFrame,
    x_col: str, y_col: str,
    title: str = 'Scatter Plot', x_label: Optional[str] = None, y_label: Optional[str] = None,
    color: str = 'blue', figsize: tuple[int, int] = (10, 6), grid: bool = True
) -> Figure:

    # Create a scatter plot
    figure, axes = plt.subplots(figsize=figsize)
    axes.scatter(source[x_col], source[y_col], color = color)
    axes.set(title = title, xlabel = x_label or x_col, ylabel = y_label or y_col)
    axes.grid(visible=grid)

    return figure


@registry.register_as('bar')
def plot_bar(
    source: pd.DataFrame,
    x_col: str, y_col: str,
    title: str = 'Bar Chart', x_label: Optional[str] = None, y_label: Optional[str] = None,
    color:str = 'blue', figsize: tuple[int, int] = (10, 6), grid: bool = True
) -> Figure:

    # Create a bar chart
    figure, axes = plt.subplots(figsize=figsize)
    axes.bar(source[x_col], source[y_col], color = color)
    axes.set(title = title, xlabel = x_label or x_col, ylabel = y_label or y_col)
    axes.grid(visible=grid)

    return figure


@registry.register_as('histogram')
def plot_histogram(
    source: pd.DataFrame,
    column: str, bins: int = 10,
    title: str = 'Histogram', x_label: Optional[str] = None, y_label: Optional[str] = None,
    color: str = 'blue', figsize: tuple[int, int] = (10, 6), grid: bool = True
) -> Figure:

    # Create a histogram
    figure, axes = plt.subplots(figsize=figsize)
    axes.hist(source[column], bins = bins, color = color)
    axes.set(title = title, xlabel = x_label or column, ylabel = y_label or 'Frequency')
    axes.grid(visible=grid)

    return figure


@registry.register_as('pie')
def plot_pie(
    source: pd.DataFrame,
    column: str, angle: float = 90,
    title: str = 'Pie Chart', figsize: tuple[int, int] = (10, 6)
) -> Figure:

    # Create a pie chart
    figure, axes = plt.subplots(figsize = figsize)
    counts = source[column].value_counts()
    axes.pie(counts, startangle = angle, labels = counts.index.to_list(), autopct = '%1.1f%%')
    axes.set(title = title)

    return figure


@registry.register_as('area')
def plot_area(
    source: pd.DataFrame,
    x_col: str, y_col: str,
    title: str = 'Area Plot', x_label: Optional[str] = None, y_label: Optional[str] = None,
    color: str = 'blue', figsize: tuple[int, int] = (10, 6), grid: bool = True
) -> Figure:

    # Create an area plot
    figure, axes = plt.subplots(figsize = figsize)
    axes.stackplot(source[x_col], source[y_col], color = color)
    axes.set(title = title, xlabel = x_label or x_col, ylabel = y_label or y_col)
    axes.grid(visible=grid)

    return figure


@registry.register_as('box')
def plot_box(
    source: pd.DataFrame,
    x_col: str, y_col: str,
    title: str = 'Box Plot', x_label: Optional[str] = None, y_label: Optional[str] = None,
    figsize: tuple[int, int] = (10, 6), grid: bool = True
) -> Figure:

    # Create a box plot
    figure, axes = plt.subplots(figsize = figsize)
    source.boxplot(column = y_col, by = x_col, ax = axes)

    axes.set(title = title, xlabel = x_label or x_col, ylabel = y_label or y_col)
    axes.grid(visible=grid)

    return figure

