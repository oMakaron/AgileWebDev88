import json, os, pandas as pd
from flask import Blueprint, jsonify, request, session, abort
from app.models import Chart, File, SharedChart
from app.extensions import db
from app.services import registry, save_to_string, read_csv
from .utils import require_login, get_user, UPLOADS_FOLDER
from sqlalchemy.exc import SQLAlchemyError

chart_api = Blueprint('chart_api', __name__, url_prefix='/charts')


@chart_api.route('/', methods=['GET'])
@require_login
def list_charts():
    charts = Chart.query.filter_by(owner_id=get_user()).all()
    return jsonify([
        {
            'id':         c.id,
            'name':       c.name,
            'spec':       c.spec,
            'file_id':    c.file_id,
            'image_data': c.image_data
        }
        for c in charts
    ])


@chart_api.route('/', methods=['POST'])
@require_login
def create_chart():
    data = request.get_json()
    name, file_id, spec = data.get('name'), data.get('file_id'), data.get('spec')

    if not (name and file_id and spec):
        abort(400, description="Missing required fields.")

    new_chart = Chart(name=name, file_id=file_id, spec=spec, owner_id=get_user())
    db.session.add(new_chart)
    db.session.commit()

    _generate_and_store_image(new_chart)

    return jsonify({
        'id':         new_chart.id,
        'image_data': new_chart.image_data
    }), 201


@chart_api.route('/<int:chart_id>', methods=['PATCH'])
@require_login
def update_chart(chart_id):
    chart = Chart.query.filter_by(id=chart_id, owner_id=get_user()).first_or_404()

    data = request.get_json()
    chart.name = data.get('name', chart.name)
    chart.spec = data.get('spec', chart.spec)
    db.session.commit()

    _generate_and_store_image(chart)

    return jsonify({
        'id':         chart.id,
        'name':       chart.name,
        'spec':       chart.spec,
        'image_data': chart.image_data
    })


@chart_api.route('/<int:chart_id>', methods=['DELETE'])
@require_login
def delete_chart(chart_id):
    chart = Chart.query.filter_by(id=chart_id, owner_id=get_user()).first_or_404()
    db.session.delete(chart)
    db.session.commit()

    return jsonify({'message': 'Chart deleted successfully.'})


def _generate_and_store_image(chart: Chart):
    try:
        file = File.query.get_or_404(chart.file_id)
        path = os.path.join('app', 'uploads', f'{file.id}.csv')
        df = pd.read_csv(path)

        spec = json.loads(chart.spec)
        graph_type = spec.get('graph_type')
        spec['source'] = df

        bound, _ = registry.functions[graph_type].bind_args(**spec)
        fig = registry.functions[graph_type].function(**bound)

        chart.image_data = save_to_string(fig)
        db.session.commit()
    except (FileNotFoundError, SQLAlchemyError, Exception) as e:
        db.session.rollback()
        raise RuntimeError(f"Failed to generate chart image: {e}")
