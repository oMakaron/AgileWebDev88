import json, os, uuid, pandas as pd
from flask import Blueprint, jsonify, request, session, abort, current_app, url_for
from app.models import Chart, File
from app.extensions import db
from app.services import registry, read_csv
from app.services.plots import save_figure_to_file
from .utils import require_login, get_user, UPLOADS_FOLDER
from sqlalchemy.exc import SQLAlchemyError

charts = Blueprint('charts', __name__, url_prefix='/charts')

@charts.route('/', methods=['GET'])
@require_login
def list_charts():
    charts = Chart.query.filter_by(owner_id=get_user()).all()
    return jsonify([
        {
            'id':         c.id,
            'name':       c.name,
            'spec':       c.spec,
            'file_id':    c.file_id,
            'image_url':  url_for('static', filename=c.image_path.replace('static/', '')) if c.image_path else None
        }
        for c in charts
    ])

@charts.route('/', methods=['POST'])
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
        'image_url':  url_for('static', filename=new_chart.image_path.replace('static/', '')) if new_chart.image_path else None
    }), 201

@charts.route('/<int:chart_id>', methods=['PATCH'])
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
        'image_url':  url_for('static', filename=chart.image_path.replace('static/', '')) if chart.image_path else None
    })

@charts.route('/<int:chart_id>', methods=['DELETE'])
@require_login
def delete_chart(chart_id):
    chart = Chart.query.filter_by(id=chart_id, owner_id=get_user()).first_or_404()

    # Delete associated image file
    if chart.image_path and os.path.exists(chart.image_path):
        os.remove(chart.image_path)

    db.session.delete(chart)
    db.session.commit()

    return jsonify({'message': 'Chart deleted successfully.'})

def _generate_and_store_image(chart: Chart):
    try:
        file = File.query.get_or_404(chart.file_id)
        path_to_csv = os.path.join(UPLOADS_FOLDER, f'{file.id}.csv')
        df = pd.read_csv(path_to_csv)

        spec = json.loads(chart.spec)
        graph_type = spec.get('graph_type')
        spec['source'] = df

        bound, _ = registry.functions[graph_type].bind_args(**spec)
        fig = registry.functions[graph_type].function(**bound)

        # Remove old image file if it exists
        if chart.image_path and os.path.exists(chart.image_path):
            os.remove(chart.image_path)

        # Save new image file and update path
        chart.image_path = save_figure_to_file(fig, chart.id)
        db.session.commit()

    except (FileNotFoundError, SQLAlchemyError, Exception) as e:
        db.session.rollback()
        raise RuntimeError(f"Failed to generate chart image: {e}")