import json, os, pandas as pd
from flask import Blueprint, jsonify, request, session
from app.models import Chart, File
from app.extensions import db
from app.services import registry, save_to_string

chart_api = Blueprint('chart_api', __name__, url_prefix='/charts')

def require_user():
    user_id = session.get('user_id')
    if not user_id:
        return None, jsonify({'error': 'Unauthorized'}), 401
    return user_id, None, None

@chart_api.route('/', methods=['GET'])
def list_charts():
    user_id, error, status = require_user()
    if error: return error, status

    charts = Chart.query.filter_by(owner_id=user_id).all()
    return jsonify([
        {
            'id':         c.id,
            'name':       c.name,
            'spec':       c.spec,
            'file_id':    c.file_id,
            'image_data': c.image_data  # 🔥 include stored image
        }
        for c in charts
    ])


@chart_api.route('/', methods=['POST'])
def create_chart():
    user_id, error, status = require_user()
    if error: return error, status

    data = request.json
    chart = Chart(
        name     = data['name'],
        spec     = data['spec'],
        file_id  = data['file_id'],
        owner_id = user_id
    )
    db.session.add(chart)
    db.session.commit()

    # generate & save the image
    _generate_and_store_image(chart)

    return jsonify({
        'id':         chart.id,
        'image_data': chart.image_data
    }), 201


@chart_api.route('/<int:chart_id>', methods=['PATCH'])
def update_chart(chart_id):
    user_id, error, status = require_user()
    if error: return error, status

    chart = Chart.query.get_or_404(chart_id)
    if chart.owner_id != user_id:
        return jsonify({'error': 'Forbidden'}), 403

    data = request.json
    chart.name = data.get('name', chart.name)
    chart.spec = data.get('spec', chart.spec)
    db.session.commit()

    # re-generate & save the image
    _generate_and_store_image(chart)

    return jsonify({
        'id':         chart.id,
        'name':       chart.name,
        'spec':       chart.spec,
        'image_data': chart.image_data
    })


def _generate_and_store_image(chart: Chart):
    """Helper to read CSV, build fig, encode to base64, store on chart."""
    # 1. load CSV from disk
    file = File.query.get_or_404(chart.file_id)
    path = os.path.join('app', 'uploads', f'{file.id}.csv')
    df = pd.read_csv(path)

    # 2. build figure
    spec = json.loads(chart.spec)
    graph_type = spec.get('graph_type')
    spec['source'] = df
    bound, _ = registry.functions[graph_type].bind_args(**spec)
    fig = registry.functions[graph_type].function(**bound)

    # 3. encode & save
    chart.image_data = save_to_string(fig)
    db.session.commit()
