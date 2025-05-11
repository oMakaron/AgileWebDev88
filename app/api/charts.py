from flask import Blueprint, jsonify, request, session
from app.models import Chart
from app.extensions import db

chart_api = Blueprint('chart_api', __name__)

def require_user():
    user_id = session.get('user_id')
    if not user_id:
        return None, jsonify({'error': 'Unauthorized'}), 401
    return user_id, None, None

@chart_api.route('/charts', methods=['GET'])
def list_charts():
    user_id, error, status = require_user()
    if error: return error, status
    charts = Chart.query.filter_by(owner_id=user_id).all()
    return jsonify([{
        'id': c.id,
        'name': c.name,
        'spec': c.spec,
        'file_id': c.file_id
    } for c in charts])

@chart_api.route('/charts/<int:chart_id>', methods=['GET'])
def get_chart(chart_id):
    user_id, error, status = require_user()
    if error: return error, status
    chart = Chart.query.get_or_404(chart_id)
    if chart.owner_id != user_id:
        return jsonify({'error': 'Forbidden'}), 403
    return jsonify({
        'id': chart.id,
        'name': chart.name,
        'spec': chart.spec,
        'file_id': chart.file_id
    })

@chart_api.route('/charts', methods=['POST'])
def create_chart():
    user_id, error, status = require_user()
    if error: return error, status
    data = request.json
    chart = Chart(
        name=data['name'],
        spec=data['spec'],
        file_id=data['file_id'],
        owner_id=user_id
    )
    db.session.add(chart)
    db.session.commit()
    return jsonify({'id': chart.id}), 201

@chart_api.route('/charts/<int:chart_id>', methods=['PATCH'])
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
    return jsonify({
        'id': chart.id,
        'name': chart.name,
        'spec': chart.spec
    })

@chart_api.route('/charts/<int:chart_id>', methods=['DELETE'])
def delete_chart(chart_id):
    user_id, error, status = require_user()
    if error: return error, status
    chart = Chart.query.get_or_404(chart_id)
    if chart.owner_id != user_id:
        return jsonify({'error': 'Forbidden'}), 403
    db.session.delete(chart)
    db.session.commit()
    return jsonify({'status': 'deleted'})
