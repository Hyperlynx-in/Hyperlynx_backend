from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from application import db
from app.models import CompanyProfile 
from datetime import datetime
from typing import Any, Dict

profile_api = Blueprint('profile_api', __name__)

@profile_api.route('/api/v1/company-profile', methods=['POST'])
@jwt_required() 
def save_company_profile():
    """
    Save or Update the Organisation Context Profile
    ---
    tags:
      - Company Profile
    security:
      - Bearer: []
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            company_name:
              type: string
            industry:
              type: string
            employee_count:
              type: string
            annual_revenue:
              type: string
            operating_regions:
              type: array
              items:
                type: string
            services_provided:
              type: array
              items:
                type: string
            regulatory_authorities:
              type: array
              items:
                type: string
            tech_stack:
              type: array
              items:
                type: string
            data_processed:
              type: array
              items:
                type: string
    responses:
      200:
        description: Profile saved successfully
      400:
        description: Invalid request payload
      500:
        description: Internal server error
    """
    data: Dict[str, Any] = request.json if request.json else {}
    if not data:
        return jsonify({"error": "No JSON payload provided."}), 400

    current_user_id = get_jwt_identity()

    try:
        profile = CompanyProfile.query.filter_by(user_id=current_user_id).first()

        if not profile:
            profile = CompanyProfile()
            profile.user_id = current_user_id
            db.session.add(profile)

        profile.company_name = data.get('company_name', '')
        profile.industry = data.get('industry', '')
        profile.employee_count = data.get('employee_count') 
        profile.annual_revenue = data.get('annual_revenue')
        
        profile.operating_regions = data.get('operating_regions', [])
        profile.services_provided = data.get('services_provided', [])
        profile.regulatory_authorities = data.get('regulatory_authorities', [])
        profile.tech_stack = data.get('tech_stack', [])
        profile.data_processed = data.get('data_processed', [])

        profile.profile_completed_at = datetime.utcnow()

        db.session.commit()
        
        return jsonify({
            "status": "success", 
            "message": "Organisation Context Profile saved successfully.",
            "profile_id": profile.id
        }), 200

    except Exception as e:
        db.session.rollback()
        print(f"Error saving profile: {e}")
        return jsonify({"error": "An internal error occurred."}), 500

@profile_api.route('/api/v1/company-profile', methods=['GET'])
@jwt_required()
def get_company_profile():
    """
    Get the current user's Organisation Context Profile
    ---
    tags:
      - Company Profile
    security:
      - Bearer: []
    responses:
      200:
        description: Returns the user's company profile
      404:
        description: Profile not found
    """
    current_user_id = get_jwt_identity()
    profile = CompanyProfile.query.filter_by(user_id=current_user_id).first()
    
    if not profile:
        return jsonify({"status": "not_found", "data": None}), 404
        
    return jsonify({
        "status": "success",
        "data": profile.to_dict()
    }), 200