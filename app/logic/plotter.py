# reads the csv and defines frames
import pandas as pd

# does the graphing
import matplotlib.pyplot as plt
from matplotlib.figure import Figure

# useful for constructing file-like objects
from io import BytesIO
from base64 import b64encode

from app.logic.specifier import Specifier


def read_csv(file) -> pd.DataFrame:
    return pd.read_csv(file, encoding='utf-8')

# TODO: Allow for more than just single-line graphs
def plot_frame(data: pd.DataFrame, specifier: Specifier) -> Figure:
    # figures contain axes, and axes contain the actual graph we can plot to
    figure, axes = plt.subplots(figsize=specifier.dimensions)
    axes.plot(data[specifier.x], data[specifier.y])
    return figure

def save_to_string(figure: Figure) -> str:
    with BytesIO() as buffer:
        figure.savefig(buffer, format='png')
        # we have to rewind so that we start reading from the begginging rather than the end
        buffer.seek(0)
        image = b64encode(buffer.read()).decode('utf-8')
    return image

