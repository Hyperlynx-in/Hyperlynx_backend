import os
from flask import Blueprint, request, jsonify
from typing import Any, Dict
from openai import OpenAI
from application import db
from app.models import RequirementNode, Framework 

grc_api = Blueprint('grc_api', __name__)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@grc_api.route('/api/v1/intelligence/auto-tag', methods=['POST'])
def auto_tag_regulatory_update():
    """
    Auto-Tag Regulatory Update
    ---
    tags:
      - GRC Intelligence
    summary: Uses AI embeddings to tag regulatory text against existing requirements
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            text:
              type: string
              description: The regulatory update text to analyze
    responses:
      200:
        description: Returns a list of mapped framework tags
      400:
        description: No regulatory text provided
      500:
        description: Error processing embeddings
    """
    # FIX: Safely retrieve JSON to satisfy Pylance
    data: Dict[str, Any] = request.get_json() or {}
    update_text = data.get('text')
    
    if not update_text:
        return jsonify({"error": "No regulatory update text provided"}), 400

    try:
        response = client.embeddings.create(
            input=update_text,
            model="text-embedding-3-small"
        )
        query_vector = response.data[0].embedding
        
        similarity_threshold = 0.65 
        
        results = db.session.query(
            RequirementNode,
            RequirementNode.embedding.cosine_distance(query_vector).label('distance')
        ).filter(
            RequirementNode.embedding.cosine_distance(query_vector) < (1 - similarity_threshold)
        ).order_by(
            'distance'
        ).limit(5).all()
        
        tags = []
        for node, distance in results:
            match_percentage = round((1 - distance) * 100, 1)
            
            framework = Framework.query.get(node.framework_id)
            
            tags.append({
                "framework_name": framework.name if framework else "Unknown",
                "framework_urn": framework.urn if framework else None,
                "requirement_ref": node.ref_id, # e.g., "Art. 5.1"
                "requirement_name": node.name,
                "confidence_score": f"{match_percentage}%"
            })
            
        return jsonify({
            "status": "success",
            "mapped_tags": tags
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500