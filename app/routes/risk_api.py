from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from typing import Dict, Any
from app.services.risk_engine import generate_risk_suggestions
from application import db
from app.models.company_profile import CompanyProfile
from app.models.risk_matrix import RiskMatrix 
from app.models.grc_context import Risk, RiskProfile 
from datetime import datetime

risk_api = Blueprint('risk_api', __name__)

@risk_api.route('/api/v1/risk/setup', methods=['GET'])
@jwt_required()
def get_risk_setup_data():
    """
    Get Risk Setup Data
    ---
    tags:
      - Risk Management
    security:
      - Bearer: []
    summary: Fetches the current Risk Profile and all available Risk Matrices
    responses:
      200:
        description: Returns risk profile and available matrices
      404:
        description: Organisation Context Profile not found
    """
    current_user_id = get_jwt_identity()
    profile = CompanyProfile.query.filter_by(user_id=current_user_id).first()
    
    if not profile:
        return jsonify({"error": "Organisation Context Profile not found."}), 404
        
    # Get or create Risk Profile
    risk_profile = RiskProfile.query.filter_by(profile_id=profile.id).first()
    if not risk_profile:
        risk_profile = RiskProfile()
        risk_profile.profile_id = profile.id
        db.session.add(risk_profile)
        db.session.commit()
        
    # Fetch all available Risk Matrices to show in a dropdown/grid UI
    matrices = RiskMatrix.query.filter_by(is_enabled=True).all()
    matrix_list = [m.to_dict() for m in matrices]
    
    return jsonify({
        "status": "success",
        "risk_profile": risk_profile.to_dict(),
        "available_matrices": matrix_list
    }), 200

@risk_api.route('/api/v1/risk/setup', methods=['POST'])
@jwt_required()
def save_risk_setup():
    """
    Save Risk Configuration
    ---
    tags:
      - Risk Management
    security:
      - Bearer: []
    summary: Saves the user's selected Risk Matrix and Appetite thresholds
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
    responses:
      200:
        description: Risk Configuration saved
      404:
        description: Profile not found
      500:
        description: Database error
    """
    current_user_id = get_jwt_identity()
    profile = CompanyProfile.query.filter_by(user_id=current_user_id).first()
    
    if not profile:
        return jsonify({"error": "Profile not found"}), 404

    data: Dict[str, Any] = request.get_json() or {}
    
    risk_profile = RiskProfile.query.filter_by(profile_id=profile.id).first()
    
    if not risk_profile:
        risk_profile = RiskProfile()
        risk_profile.profile_id = profile.id
        db.session.add(risk_profile)
    
    try:
        risk_profile.risk_matrix_id = data.get('risk_matrix_id')
        risk_profile.risk_appetite = data.get('risk_appetite')
        risk_profile.risk_tolerance = data.get('risk_tolerance')
        
        db.session.commit()
        return jsonify({"status": "success", "message": "Risk Configuration saved!"}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
      
@risk_api.route('/api/v1/risks', methods=['GET'])
@jwt_required()
def get_risks():
    """
    Get All Risks
    ---
    tags:
      - Risk Management
    security:
      - Bearer: []
    summary: Retrieve the risk register for the current profile
    responses:
      200:
        description: Array of risks
      404:
        description: Profile not found
    """
    current_user_id = get_jwt_identity()
    profile = CompanyProfile.query.filter_by(user_id=current_user_id).first()
    
    if not profile:
        return jsonify({"error": "Profile not found"}), 404
        
    risks = Risk.query.filter_by(profile_id=profile.id).order_by(Risk.created_at.desc()).all()
    return jsonify({"status": "success", "risks": [r.to_dict() for r in risks]}), 200

@risk_api.route('/api/v1/risks', methods=['POST'])
@jwt_required()
def add_risk():
    """
    Add a Risk
    ---
    tags:
      - Risk Management
    security:
      - Bearer: []
    summary: Manually log a new risk entry
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
    responses:
      201:
        description: Risk created successfully
      404:
        description: Profile not found
      500:
        description: Database error
    """
    current_user_id = get_jwt_identity()
    profile = CompanyProfile.query.filter_by(user_id=current_user_id).first()
    
    if not profile:
        return jsonify({"error": "Profile not found"}), 404
        
    data: Dict[str, Any] = request.get_json() or {}
    
    try:
        # Generate a simple Risk ID (e.g., R-001, R-002)
        risk_count = Risk.query.filter_by(profile_id=profile.id).count()
        new_risk_id = f"R-{str(risk_count + 1).zfill(3)}"
        
        # Calculate score (Likelihood * Impact)
        l = int(data.get('likelihood', 1))
        i = int(data.get('impact', 1))
        
        new_risk = Risk()
        new_risk.profile_id = profile.id
        new_risk.risk_id = new_risk_id
        new_risk.name = data.get('name')
        new_risk.category = data.get('category')
        new_risk.likelihood = l
        new_risk.impact = i
        new_risk.score = (l * i)
        new_risk.status = "Open"
        new_risk.owner = data.get('owner', 'Unassigned')
        
        db.session.add(new_risk)
        db.session.commit()
        
        return jsonify({"status": "success", "risk": new_risk.to_dict()}), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
    
@risk_api.route('/api/v1/risks/suggest', methods=['GET'])
@jwt_required()
def suggest_risks():
    """
    Suggest AI Risks
    ---
    tags:
      - Risk Management
    security:
      - Bearer: []
    summary: Generate AI risk suggestions based on company context
    responses:
      200:
        description: Returns AI risk suggestions
      404:
        description: Profile not found
      500:
        description: AI generation failed
    """
    current_user_id = get_jwt_identity()
    profile = CompanyProfile.query.filter_by(user_id=current_user_id).first()
    
    if not profile:
        return jsonify({"error": "Profile not found. Complete Intelligence Setup first."}), 404
        
    risk_profile = RiskProfile.query.filter_by(profile_id=profile.id).first()
    active_matrix = None
    if risk_profile and risk_profile.risk_matrix_id:
        matrix_record = RiskMatrix.query.get(risk_profile.risk_matrix_id)
        if matrix_record:
            active_matrix = matrix_record.to_dict()

    existing_risks = Risk.query.filter_by(profile_id=profile.id).all()
    existing_risk_names = [r.name for r in existing_risks]

    try:
        result = generate_risk_suggestions(profile.to_dict(), active_matrix, existing_risk_names)
        
        profile.risk_ai_run_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({"status": "success", "suggestions": result.get("suggestions", [])}), 200
    except Exception as e:
        db.session.rollback() 
        return jsonify({"error": "Failed to generate AI suggestions"}), 500