import uuid
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from typing import Dict, Any
from application import db
from app.models.company_profile import CompanyProfile
from app.models.grc_context import MetricDefinition, MetricSample

metrics_api = Blueprint('metrics_api', __name__)

@metrics_api.route('/api/v1/metrics', methods=['GET'])
@jwt_required()
def get_metrics():
    """
    Get All Metrics
    ---
    tags:
      - Metrics
    security:
      - Bearer: []
    responses:
      200:
        description: List of metrics with their latest recorded sample
      404:
        description: Organisation Profile not found
    """
    current_user_id = get_jwt_identity()
    profile = CompanyProfile.query.filter_by(user_id=current_user_id).first()
    
    if not profile:
        return jsonify({"error": "Organisation Profile not found"}), 404

    definitions = MetricDefinition.query.all()
    
    metrics_data = []
    for defi in definitions:
        latest_sample = MetricSample.query.filter_by(
            profile_id=profile.id, 
            definition_id=defi.id
        ).order_by(MetricSample.measured_at.desc()).first()
        
        metrics_data.append({
            "id": defi.id,
            "name": defi.name,
            "description": defi.description,
            "category": defi.category,
            "unit": defi.unit,
            "target_value": defi.target_value,
            "operator": defi.operator,
            "periodicity": defi.periodicity,
            "current_value": latest_sample.value if latest_sample else None,
            "last_measured": latest_sample.measured_at.isoformat() if latest_sample else None,
            "notes": latest_sample.notes if latest_sample else None
        })

    return jsonify({"status": "success", "metrics": metrics_data}), 200

@metrics_api.route('/api/v1/metrics/<definition_id>/sample', methods=['POST'])
@jwt_required()
def add_metric_sample(definition_id):
    """
    Add a Metric Sample
    ---
    tags:
      - Metrics
    security:
      - Bearer: []
    parameters:
      - in: path
        name: definition_id
        required: true
        type: string
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            value:
              type: number
            notes:
              type: string
    responses:
      201:
        description: Measurement recorded
      400:
        description: Value is required
      404:
        description: Profile not found
    """
    current_user_id = get_jwt_identity()
    profile = CompanyProfile.query.filter_by(user_id=current_user_id).first()
    
    if not profile:
        return jsonify({"error": "Organisation Profile not found"}), 404
        
    data: Dict[str, Any] = request.get_json() or {}
    
    if 'value' not in data:
        return jsonify({"error": "Value is required"}), 400
        
    try:
        new_sample = MetricSample()
        new_sample.id = str(uuid.uuid4())
        new_sample.profile_id = profile.id
        new_sample.definition_id = definition_id
        new_sample.value = float(data['value'])
        new_sample.notes = data.get('notes', '')
        
        db.session.add(new_sample)
        db.session.commit()
        return jsonify({"status": "success", "message": "Measurement recorded"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500