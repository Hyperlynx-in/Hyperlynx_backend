from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from application import db
from app.models.company_profile import CompanyProfile
from app.models.risk_matrix import RiskMatrix 
from app.models.grc_context import RiskProfile 

risk_api = Blueprint('risk_api', __name__)

@risk_api.route('/api/v1/risk/setup', methods=['GET'])
@jwt_required()
def get_risk_setup_data():
    """
    Fetches the current Risk Profile and all available Risk Matrices 
    (3x3, 4x4, 5x5) for the UI to render.
    """
    current_user_id = get_jwt_identity()
    profile = CompanyProfile.query.filter_by(user_id=current_user_id).first()
    
    if not profile:
        return jsonify({"error": "Organisation Context Profile not found."}), 404
        
    # Get or create Risk Profile
    risk_profile = RiskProfile.query.filter_by(profile_id=profile.id).first()
    if not risk_profile:
        risk_profile = RiskProfile(profile_id=profile.id)
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
    Saves the user's selected Risk Matrix and Appetite thresholds.
    """
    current_user_id = get_jwt_identity()
    profile = CompanyProfile.query.filter_by(user_id=current_user_id).first()
    data = request.get_json()
    
    risk_profile = RiskProfile.query.filter_by(profile_id=profile.id).first()
    
    try:
        risk_profile.risk_matrix_id = data.get('risk_matrix_id')
        risk_profile.risk_appetite = data.get('risk_appetite')
        risk_profile.risk_tolerance = data.get('risk_tolerance')
        
        db.session.commit()
        return jsonify({"status": "success", "message": "Risk Configuration saved!"}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500