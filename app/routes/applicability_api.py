import uuid
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func  # <-- ADDED THIS
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
    current_user_id = get_jwt_identity()
    profile = CompanyProfile.query.filter_by(user_id=current_user_id).first()
    
    if not profile:
        return jsonify({"error": "Organisation Context Profile not found."}), 404
        
    counts_query = db.session.query(
        Framework.id, 
        func.count(RequirementNode.id)
    ).outerjoin(
        RequirementNode, Framework.id == RequirementNode.framework_id
    ).group_by(Framework.id).all()
    

    controls_map = {str(fw_id): count for fw_id, count in counts_query}

    all_frameworks = Framework.query.all()
    frameworks_payload = []
    
    for f in all_frameworks:
        frameworks_payload.append({
            "id": str(f.id), 
            "name": f.name, 
            "description": getattr(f, 'description', ''),
            "controls_count": controls_map.get(str(f.id), 0) 
        })

    saved_frameworks = OrganisationFramework.query.filter_by(profile_id=profile.id).all()
    
    if saved_frameworks:
        print(f"✅ Loaded {len(saved_frameworks)} saved frameworks instantly!")
        valid_suggestions = []
        for sf in saved_frameworks:
            matching_fw = next((fw for fw in frameworks_payload if fw['id'] == str(sf.framework_id)), None)
            if matching_fw:
                valid_suggestions.append({
                    "framework_id": str(sf.framework_id),
                    "name": matching_fw["name"],
                    "category": "Saved Baseline", 
                    "confidence": 100,
                    "rationale": sf.rationale,
                    "controls": matching_fw["controls_count"],
                    "is_mandatory": sf.is_mandatory,
                    "enabled": True  
                })
                
        return jsonify({
            "status": "success",
            "suggestions": valid_suggestions,
            "catalog": frameworks_payload 
        }), 200

    print("🤖 No baseline found. Booting up AI applicability engine...")
    result = generate_framework_suggestions(profile.to_dict(), frameworks_payload)
    raw_suggestions = result.get("suggestions", [])
    
    valid_suggestions = []
    for sug in raw_suggestions:
        matching_fw = next((fw for fw in frameworks_payload if fw['id'] == str(sug.get('framework_id'))), None)
        if matching_fw:
            sug['controls'] = matching_fw['controls_count']
            sug['enabled'] = sug.get('is_mandatory', False) or sug.get('confidence', 0) >= 80
            valid_suggestions.append(sug)
        else:
            print(f"⚠️ Blocked AI hallucination for framework: {sug.get('name', 'Unknown')}")

    return jsonify({
        "status": "success",
        "suggestions": valid_suggestions,
        "catalog": frameworks_payload 
    }), 200

@applicability_api.route('/api/v1/applicability/save', methods=['POST'])
@jwt_required()
def save_frameworks():
    current_user_id = get_jwt_identity()
    profile = CompanyProfile.query.filter_by(user_id=current_user_id).first()
    data = request.json.get('selected_frameworks', [])
    
    try:
        OrganisationFramework.query.filter_by(profile_id=profile.id).delete()
        
        for fw in data:
            new_fw = OrganisationFramework(
                id=str(uuid.uuid4()), 
                profile_id=profile.id,
                framework_id=fw['framework_id'],
                is_mandatory=fw.get('is_mandatory', False),
                rationale=fw.get('rationale', fw.get('reason', 'Manually saved by user.'))
            )
            db.session.add(new_fw)
            
        db.session.commit()
        return jsonify({"status": "success"}), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ ERROR SAVING FRAMEWORKS: {str(e)}")
        return jsonify({"error": "Failed to save frameworks to database"}), 500