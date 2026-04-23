from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from application import db
from app.models.company_profile import CompanyProfile
from app.models.grc_context import RiskProfile, MetricDefinition, MetricSample
from app.models.organisation_framework import OrganisationFramework
from app.models.framework import Framework
from sqlalchemy import func

context_report_api = Blueprint('context_report_api', __name__)

@context_report_api.route('/api/v1/context/master-report', methods=['GET'])
@jwt_required()
def get_master_report():
    current_user_id = get_jwt_identity()
    
    # 1. Get Business Context
    profile = CompanyProfile.query.filter_by(user_id=current_user_id).first()
    if not profile:
        return jsonify({"error": "Organisation Profile not found"}), 404

    # 2. Get Regulatory Baseline (Frameworks)
    saved_frameworks = OrganisationFramework.query.filter_by(profile_id=profile.id).all()
    frameworks_data = []
    for sf in saved_frameworks:
        fw = Framework.query.get(sf.framework_id)
        if fw:
            frameworks_data.append({
                "name": fw.name,
                "rationale": sf.rationale,
                "is_mandatory": sf.is_mandatory
            })

    # 3. Get Risk Posture
    risk_profile = RiskProfile.query.filter_by(profile_id=profile.id).first()
    risk_data = None
    if risk_profile:
        risk_data = {
            "appetite": risk_profile.risk_appetite,
            "tolerance": risk_profile.risk_tolerance,
            "matrix_configured": bool(risk_profile.risk_matrix_id)
        }

    # 4. Get Current Metrology (Latest Samples)
    definitions = MetricDefinition.query.all()
    metrics_data = []
    for defi in definitions:
        latest = MetricSample.query.filter_by(
            profile_id=profile.id, 
            definition_id=defi.id
        ).order_by(MetricSample.measured_at.desc()).first()
        
        if latest:
            metrics_data.append({
                "name": defi.name,
                "category": defi.category,
                "target": f"{defi.operator} {defi.target_value}{defi.unit}",
                "current": f"{latest.value}{defi.unit}",
                "status": "Meeting" if (
                    (defi.operator == '>=' and latest.value >= defi.target_value) or
                    (defi.operator == '<=' and latest.value <= defi.target_value)
                ) else "Failing"
            })

    # Assemble the Master Output
    report = {
        "organization": profile.to_dict(),
        "regulatory_baseline": frameworks_data,
        "risk_posture": risk_data,
        "key_metrics": metrics_data
    }

    return jsonify({"status": "success", "report": report}), 200