from flask import Blueprint
from .files import file_api
from .charts import chart_api
from .plots import plots

api = Blueprint('api', __name__, url_prefix='/api')
api.register_blueprint(file_api)
api.register_blueprint(chart_api)
api.register_blueprint(plots)
