from flask import Blueprint
from .files import files
from .charts import charts
from .plots import plots
from .friends import friends
from .notifications import notifications

api = Blueprint('api', __name__, url_prefix='/api')
api.register_blueprint(files)
api.register_blueprint(charts)
api.register_blueprint(plots)
api.register_blueprint(friends)
api.register_blueprint(notifications)