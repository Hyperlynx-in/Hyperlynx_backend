from datetime import datetime
import uuid
from flask import Blueprint, request, jsonify
from sqlalchemy import func
from flask_jwt_extended import jwt_required, get_jwt_identity
from typing import Any, Dict, List

from application import db
from app.models.company_profile import CompanyProfile
from app.models.framework import Framework 
from app.models.organisation_framework import OrganisationFramework
from app.services.applicability_engine import generate_framework_suggestions
from app.models import RequirementNode 

applicability_api = Blueprint('applicability_api', __name__)

@applicability_api.route('/api/v1/applicability/suggest', methods=['GET'])
@jwt_required()
def suggest_frameworks():
    """
    Suggest or Retrieve Compliance Frameworks
    ---
    tags:
      - Applicability Engine
    security:
      - Bearer: []
    parameters:
      - in: query
        name: force
        type: boolean
        required: false
        description: Set to true to bypass saved frameworks and force an AI re-run.
    responses:
      200:
        description: Returns a list of suggested frameworks and the master catalog.
      404:
        description: Organisation profile not found.
      500:
        description: AI generation failed.
    """
    current_user_id = get_jwt_identity()
    profile = CompanyProfile.query.filter_by(user_id=current_user_id).first()
    force_rerun = request.args.get('force', 'false').lower() == 'true'
    
    if not profile:
        return jsonify({"error": "Organisation Context Profile not found."}), 404
        
    counts_query = db.session.query(Framework.id, func.count(RequirementNode.id)).outerjoin(RequirementNode, Framework.id == RequirementNode.framework_id).group_by(Framework.id).all()
    controls_map = {str(fw_id): count for fw_id, count in counts_query}

    all_frameworks = Framework.query.all()
    frameworks_payload = [{"id": str(f.id), "name": f.name, "description": getattr(f, 'description', ''), "controls_count": controls_map.get(str(f.id), 0)} for f in all_frameworks]

    saved_frameworks = OrganisationFramework.query.filter_by(profile_id=profile.id).all()
    
    if saved_frameworks and not force_rerun:
        valid_suggestions = []
        for sf in saved_frameworks:
            matching_fw = next((fw for fw in frameworks_payload if fw['id'] == str(sf.framework_id)), None)
            if matching_fw:
                valid_suggestions.append({
                    "framework_id": str(sf.framework_id),
                    "name": matching_fw["name"],
                    "category": "Saved Baseline", 
                    "confidence": 100,
                    "reason": sf.rationale,
                    "controls": matching_fw["controls_count"],
                    "is_mandatory": sf.is_mandatory,
                    "action": "Keep",
                    "enabled": True  
                })
        return jsonify({"status": "success", "suggestions": valid_suggestions, "catalog": frameworks_payload}), 200

    try:
        current_fws = [{"id": str(sf.framework_id), "rationale": sf.rationale} for sf in saved_frameworks]
        result = generate_framework_suggestions(profile.to_dict(), frameworks_payload, current_fws)
        
        profile.framework_ai_run_at = datetime.utcnow()
        db.session.commit()
        
        valid_suggestions = []
        for sug in result.get("suggestions", []):
            matching_fw = next((fw for fw in frameworks_payload if fw['id'] == str(sug.get('framework_id'))), None)
            if matching_fw:
                sug['controls'] = matching_fw['controls_count']
                sug['enabled'] = sug.get('action') != 'Remove' 
                valid_suggestions.append(sug)

        return jsonify({"status": "success", "suggestions": valid_suggestions, "catalog": frameworks_payload}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to generate AI framework suggestions", "details": str(e)}), 500


@applicability_api.route('/api/v1/applicability/save', methods=['POST'])
@jwt_required()
def save_frameworks():
    """
    Save the selected Applicability Baseline
    ---
    tags:
      - Applicability Engine
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
            selected_frameworks:
              type: array
              items:
                type: object
                properties:
                  framework_id:
                    type: string
                  is_mandatory:
                    type: boolean
                  reason:
                    type: string
    responses:
      200:
        description: Baseline saved successfully.
      400:
        description: Invalid request payload.
      404:
        description: Profile not found.
      500:
        description: Database save failed.
    """
    current_user_id = get_jwt_identity()
    profile = CompanyProfile.query.filter_by(user_id=current_user_id).first()
    
    if not profile:
        return jsonify({"error": "Organisation Profile not found."}), 404
        
    req_data: Dict[str, Any] = request.json if request.json else {}
    data: List[Dict[str, Any]] = req_data.get('selected_frameworks', [])
    
    try:
        OrganisationFramework.query.filter_by(profile_id=profile.id).delete()
        
        for fw in data:
            new_fw = OrganisationFramework()
            new_fw.id = str(uuid.uuid4())
            new_fw.profile_id = profile.id
            new_fw.framework_id = fw.get('framework_id')
            new_fw.is_mandatory = fw.get('is_mandatory', False)
            new_fw.rationale = fw.get('reason', 'Manually saved by user.')
            
            db.session.add(new_fw)
            
        db.session.commit()
        return jsonify({"status": "success"}), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ ERROR SAVING FRAMEWORKS: {str(e)}")
        return jsonify({"error": "Failed to save frameworks to database"}), 500