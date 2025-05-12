from os import path

from flask import Blueprint, Response, abort, jsonify, request

from ..models import Chart, SharedChart
from ..services import Parser, ParseError, BindError, registry, read_csv, save_to_string
from ..extensions import db
from .utils import require_login, get_user, UPLOADS_FOLDER


charts = Blueprint('charts', __name__)


def make_response_from_chart(chart: Chart, status: int = 200) -> Response:
    response = jsonify({
        'id': chart.id,
        'name': chart.name,
        'file_id': chart.file_id,
        'spec': chart.spec,
    })
    response.status_code = status
    return response


@charts.route('/', methods=['GET'])
@require_login
def get_all_charts() -> Response:
    charts = Chart.query.filter_by(owner_id=get_user()).all()
    return jsonify([{ 'id': chart.id, 'name': chart.name } for chart in charts])


@charts.route('/', methods=['POST'])
@require_login
def make_new_chart() -> Response:
    data = request.get_json()
    name, file_id, spec = data.get('name'), data.get('file_id'), data.get('spec')

    if not (name and file_id and spec):
        abort(400, description="Missing required fields.")

    new_chart = Chart(name=name, file_id=file_id, spec=spec, owner_id=get_user()) # type: ignore
    db.session.add(new_chart)
    db.session.commit()

    return make_response_from_chart(new_chart, 201)


@charts.route('/<int:chart_id>/', methods=['GET'])
@require_login
def get_chart(chart_id: int) -> Response:
    chart = Chart.query.filter_by(id=chart_id, owner_id=get_user()).first_or_404()
    return make_response_from_chart(chart)


@charts.route('/<int:chart_id>/', methods=['PUT'])
@require_login
def edit_chart(chart_id: int) -> Response:
    chart = Chart.query.filter_by(id=chart_id, owner_id=get_user()).first_or_404()

    data = request.get_json()

    chart.name = data.get('name', chart.name)
    chart.file_id = data.get('file_id', chart.file_id)
    chart.spec = data.get('spec', chart.spec)

    db.session.commit()

    return make_response_from_chart(chart)


@charts.route('/<int:chart_id>/', methods=['DELETE'])
@require_login
def delete_chart(chart_id: int) -> Response:
    chart = Chart.query.filter_by(id=chart_id, owner_id=get_user()).first_or_404()

    db.session.delete(chart)
    db.session.commit()

    response = jsonify({'message': 'Chart deleted successfully.'})
    response.status_code = 200

    return response


@charts.route('/<int:chart_id>/view/', methods=['GET'])
@require_login
def get_chart_view(chart_id: int) -> Response:
    chart = Chart.query.get_or_404(chart_id)

    if chart.owner_id != get_user() and not any(share.user_id == get_user() for share in chart.shared_with):
        abort(403, description="You do not have permission to view this chart.")

    try:
        parsed_args = Parser.parse_string(chart.spec)
    except ParseError as error:
        response = jsonify({ 'error': 'Poorly formatted chart spec.', 'details': str(error) })
        response.status_code = 400
        return response

    chart_type = parsed_args.pop('type')
    chart_type = chart_type if not isinstance(chart_type, list) else chart_type[0]

    file_path = path.join(UPLOADS_FOLDER, f"{chart.file_id}.csv")
    if not path.exists(file_path):
        abort(404, description="File could not be located internally.")

    try:
        with open(file_path, "r") as file:
            data_frame = read_csv(file)
    except Exception:
        response = jsonify({'error': 'Internal server error.'})
        response.status_code = 500
        return response

    plotter = registry.functions[chart_type]

    try:
        bound, unbound = plotter.bind_args(source=data_frame, **parsed_args)
    except BindError as error:
        response = jsonify({
            'error': 'Chart spec is missing required arguments.',
            'missing': error.missing(),
            'unbound': error.unbound(),
        })
        response.status_code = 400
        return response

    figure = plotter.function(**bound)
    image = save_to_string(figure)

    image_uri = f"data:image/png;base64,{image}"

    return jsonify({'chart_view': image_uri, 'unbound': unbound})

