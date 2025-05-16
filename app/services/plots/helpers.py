# reads the csv and defines frames
import pandas as pd
import os, uuid
from flask import current_app

# does the graphing
from matplotlib.figure import Figure

# useful for constructing file-like objects
from io import BytesIO
from base64 import b64encode


def read_csv(file) -> pd.DataFrame:
    return pd.read_csv(file, encoding='utf-8')

def save_to_string(figure: Figure) -> str:
    with BytesIO() as buffer:
        figure.savefig(buffer, format='png')
        # we have to rewind so that we start reading from the beginning rather than the end
        buffer.seek(0)
        image = b64encode(buffer.read()).decode('utf-8')
    return image

def save_figure_to_file(fig: Figure, chart_id: int) -> str:
    folder = current_app.config['IMAGE_FOLDER']
    os.makedirs(folder, exist_ok=True)
    fname = f"chart_{chart_id}_{uuid.uuid4().hex[:8]}.png"
    path = os.path.join(folder, fname)
    fig.savefig(path, bbox_inches='tight')
    return fname
