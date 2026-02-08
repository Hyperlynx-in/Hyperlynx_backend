"""Requirement mapping routes"""
from flask import jsonify, request
from application import db
from app.models import RequirementMappingSet, RequirementMapping


def register_mapping_routes(app):
    """Register requirement mapping routes"""
    
    @app.route('/api/requirement-mapping-sets/', methods=['GET'])
    def list_requirement_mappings():
        """
        List Requirement Mappings
        ---
        tags:
          - Requirement Mappings
        summary: List all requirement mappings (framework relationships)
        description: Examples - ISO 27001 ↔ NIST CSF, NIST CSF v1.1 ↔ NIST CSF v2.0
        parameters:
          - name: search
            in: query
            type: string
            description: Search mappings
        responses:
          200:
            description: Array of mapping sets
        """
        query = RequirementMappingSet.query
        
        if search := request.args.get('search'):
            query = query.filter(
                db.or_(
                    RequirementMappingSet.name.ilike(f'%{search}%'),
                    RequirementMappingSet.description.ilike(f'%{search}%'),
                    RequirementMappingSet.source_framework_urn.ilike(f'%{search}%'),
                    RequirementMappingSet.target_framework_urn.ilike(f'%{search}%')
                )
            )
        
        mapping_sets = query.all()
        return jsonify({
            'count': len(mapping_sets),
            'results': [ms.to_dict() for ms in mapping_sets]
        }), 200
    
    
    @app.route('/api/requirement-mapping-sets/<path:mapping_id>/', methods=['GET'])
    def get_requirement_mapping_set(mapping_id):
        """
        Get Mapping Set Details
        ---
        tags:
          - Requirement Mappings
        summary: Get specific mapping between two frameworks
        description: Returns mapping set with source/target framework URNs and individual requirement mappings
        parameters:
          - name: mapping_id
            in: path
            required: true
            type: string
        responses:
          200:
            description: Mapping set object with individual mappings
        """
        mapping_set = RequirementMappingSet.query.filter(
            db.or_(
                RequirementMappingSet.id == mapping_id,
                RequirementMappingSet.urn == mapping_id
            )
        ).first()
        
        if not mapping_set:
            return jsonify({'error': 'Mapping set not found'}), 404
        
        return jsonify(mapping_set.to_dict(include_mappings=True)), 200
    
    
    @app.route('/api/requirement-mapping-sets/', methods=['POST'])
    def create_requirement_mapping_set():
        """
        Create Mapping Set
        ---
        tags:
          - Requirement Mappings
        summary: Create new requirement mapping set
        responses:
          201:
            description: Mapping set created
        """
        data = request.get_json()
        urn = data.get('urn', f"urn:custom:mapping:{data.get('ref_id')}")
        
        mapping_set = RequirementMappingSet(
            id=urn,
            urn=urn,
            ref_id=data.get('ref_id'),
            name=data.get('name'),
            description=data.get('description'),
            source_framework_urn=data.get('source_framework_urn'),
            target_framework_urn=data.get('target_framework_urn')
        )
        
        db.session.add(mapping_set)
        db.session.commit()
        
        return jsonify(mapping_set.to_dict()), 201
    
    
    @app.route('/api/requirement-mapping-sets/<path:mapping_id>/', methods=['PUT', 'PATCH'])
    def update_requirement_mapping_set(mapping_id):
        """Update Mapping Set --- tags: [Requirement Mappings]"""
        mapping_set = RequirementMappingSet.query.filter(
            db.or_(
                RequirementMappingSet.id == mapping_id,
                RequirementMappingSet.urn == mapping_id
            )
        ).first()
        
        if not mapping_set:
            return jsonify({'error': 'Mapping set not found'}), 404
        
        data = request.get_json()
        for key in ['name', 'description', 'source_framework_urn', 'target_framework_urn']:
            if key in data:
                setattr(mapping_set, key, data[key])
        
        db.session.commit()
        return jsonify(mapping_set.to_dict()), 200
    
    
    @app.route('/api/requirement-mapping-sets/<path:mapping_id>/', methods=['DELETE'])
    def delete_requirement_mapping_set(mapping_id):
        """Delete Mapping Set --- tags: [Requirement Mappings]"""
        mapping_set = RequirementMappingSet.query.filter(
            db.or_(
                RequirementMappingSet.id == mapping_id,
                RequirementMappingSet.urn == mapping_id
            )
        ).first()
        
        if mapping_set:
            db.session.delete(mapping_set)
            db.session.commit()
        
        return jsonify({'status': 'success'}), 200
