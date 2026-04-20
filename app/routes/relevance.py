from flask import Blueprint, request, jsonify
from application import db
from app.models import CompanyProfile
from app.services.relevance_engine import calculate_relevance_score

relevance_api = Blueprint('relevance_api', __name__)

@relevance_api.route('/api/v1/relevance/score', methods=['POST'])
def get_relevance():
    data = request.json
    update_text = data.get('update_text')
    profile_id = data.get('profile_id')
    
    if not update_text or not profile_id:
        return jsonify({"error": "Missing update_text or profile_id"}), 400
        
    profile = CompanyProfile.query.get(profile_id)
    if not profile:
        return jsonify({"error": "Company Profile not found"}), 404
        
    relevance_data = calculate_relevance_score(update_text, profile.to_dict())
    
    
    return jsonify({
        "status": "success",
        "data": relevance_data
    }), 200