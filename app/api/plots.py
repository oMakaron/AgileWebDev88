from flask import Blueprint, Response, abort, jsonify

from ..services import registry


plots = Blueprint('plots', __name__)


@plots.route('/', methods=["GET"])
def get_plots() -> Response:
    return jsonify(registry.list_plots())


@plots.route('/<plot>/', methods=["GET"])
def get_plot(plot: str) -> Response:
    if plot == 'common':
        return jsonify(registry.list_common_args())

    plotter = registry.functions.get(plot)
    if not plotter:
        abort(404, description="Invalid chart type.")

    return jsonify(plotter.list_args())

