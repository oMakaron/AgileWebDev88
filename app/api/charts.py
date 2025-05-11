from flask import Blueprint, Response


charts = Blueprint('charts', __name__)


@charts.route('/', methods=['GET'])
def get_all_charts() -> Response:
    ...


@charts.route('/', methods=['POST'])
def make_new_chart() -> Response:
    ...


@charts.route('/<int:chart_id>/', methods=['GET'])
def get_chart(chart_id: int) -> Response:
    ...


@charts.route('/<int:chart_id>/', methods=['PUT'])
def edit_chart(chart_id: int) -> Response:
    ...


@charts.route('/<int:chart_id>/view/', methods=['GET'])
def get_chart_view(chart_id: int) -> Response:
    ...

