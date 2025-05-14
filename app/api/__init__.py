from flask import Blueprint
from .files import files
from .charts import charts
from .plots import plots

api = Blueprint('api', __name__, url_prefix='/api')
api.register_blueprint(files)
api.register_blueprint(charts)
api.register_blueprint(plots)
