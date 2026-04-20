from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from application import db
from app.models.company_profile import CompanyProfile 

profile_api = Blueprint('profile_api', __name__)

@profile_api.route('/api/v1/company-profile', methods=['POST'])
@jwt_required() 
def save_company_profile():
    data = request.json
    
    current_user_id = get_jwt_identity()

    try:
        profile = CompanyProfile.query.filter_by(user_id=current_user_id).first()

        if not profile:
            profile = CompanyProfile(user_id=current_user_id)
            db.session.add(profile)

        profile.company_name = data.get('company_name', '')
        profile.industry = data.get('industry', '')
        profile.employee_count = data.get('employee_count') 
        profile.annual_revenue = data.get('annual_revenue')
        profile.operating_regions = data.get('operating_regions', [])
        profile.tech_stack = data.get('tech_stack', [])
        profile.data_processed = data.get('data_processed', [])

        db.session.commit()
        
        return jsonify({
            "status": "success", 
            "message": "Company profile saved.",
            "profile_id": profile.id
        }), 200

    except Exception as e:
        db.session.rollback()
        print(f"Error saving profile: {str(e)}")
        return jsonify({"error": "Failed to save profile to database."}), 500

@profile_api.route('/api/v1/company-profile', methods=['GET'])
@jwt_required()
def get_company_profile():
    """Fetches the current user's company profile so the wizard can pre-fill data if they return"""
    current_user_id = get_jwt_identity()
    profile = CompanyProfile.query.filter_by(user_id=current_user_id).first()
    
    if not profile:
        return jsonify({"status": "not_found", "data": None}), 404
        
    return jsonify({
        "status": "success",
        "data": profile.to_dict()
    }), 200