from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from application import db
from app.models.framework import Framework 

frameworks_api = Blueprint('frameworks_api', __name__)

@frameworks_api.route('/api/v1/frameworks', methods=['GET'])
@jwt_required()
def get_all_frameworks():
    """
    Retrieves the master catalog of all available frameworks in the database.
    """
    try:
        all_frameworks = Framework.query.all()
        
        frameworks_list = []
        for f in all_frameworks:
            controls_count = len(f.requirements) if hasattr(f, 'requirements') else 0
            
            frameworks_list.append({
                "id": f.id,
                "name": f.name,
                "description": getattr(f, 'description', 'No description available.'),
                "version": getattr(f, 'version', '1.0'),
                "controls_count": controls_count
            })
            
        return jsonify({
            "status": "success",
            "data": frameworks_list
        }), 200
        
    except Exception as e:
        print(f"Error fetching frameworks: {str(e)}")
        return jsonify({"error": "Failed to fetch frameworks catalog."}), 500