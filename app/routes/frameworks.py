"""Frameworks API routes"""
from flask import jsonify, request
from application import db
from app.models import Framework, RequirementNode


def register_framework_routes(app):
    """Register framework API routes"""
    
    @app.route('/api/frameworks/', methods=['GET'])
    def list_frameworks():
        """
        List Frameworks
        ---
        tags:
          - Frameworks
        summary: List all frameworks in the system
        parameters:
          - name: name
            in: query
            type: string
            description: Filter by name
          - name: description
            in: query
            type: string
            description: Filter by description
          - name: id
            in: query
            type: string
            description: Filter by ID
          - name: search
            in: query
            type: string
            description: Search in name and description
          - name: limit
            in: query
            type: integer
            default: 20
          - name: offset
            in: query
            type: integer
            default: 0
        responses:
          200:
            description: Array of frameworks with basic info
        """
        query = Framework.query
        
        # Filters
        if name := request.args.get('name'):
            query = query.filter(Framework.name.ilike(f'%{name}%'))
        if description := request.args.get('description'):
            query = query.filter(Framework.description.ilike(f'%{description}%'))
        if id_filter := request.args.get('id'):
            query = query.filter_by(id=id_filter)
        
        # Search
        if search := request.args.get('search'):
            query = query.filter(
                db.or_(
                    Framework.name.ilike(f'%{search}%'),
                    Framework.description.ilike(f'%{search}%'),
                    Framework.ref_id.ilike(f'%{search}%')
                )
            )
        
        # Pagination
        limit = int(request.args.get('limit', 20))
        offset = int(request.args.get('offset', 0))
        
        total = query.count()
        frameworks = query.limit(limit).offset(offset).all()
        
        return jsonify({
            'count': total,
            'results': [f.to_dict() for f in frameworks]
        }), 200
    
    
    @app.route('/api/frameworks/<path:framework_id>/', methods=['GET'])
    def get_framework(framework_id):
        """
        Get Framework Details
        ---
        tags:
          - Frameworks
        summary: Get single framework details
        parameters:
          - name: framework_id
            in: path
            required: true
            type: string
        responses:
          200:
            description: Framework object with metadata
        """
        framework = Framework.query.filter(
            db.or_(
                Framework.id == framework_id,
                Framework.urn == framework_id
            )
        ).first()
        
        if not framework:
            return jsonify({'error': 'Framework not found'}), 404
        
        return jsonify(framework.to_dict()), 200
    
    
    @app.route('/api/frameworks/<path:framework_id>/tree/', methods=['GET'])
    def get_framework_tree(framework_id):
        """
        Get Framework Tree (Requirements)
        ---
        tags:
          - Frameworks
        summary: Get hierarchical tree of all requirements
        description: Display requirements in compliance assessment UI
        parameters:
          - name: framework_id
            in: path
            required: true
            type: string
        responses:
          200:
            description: Nested requirement structure
        """
        framework = Framework.query.filter(
            db.or_(
                Framework.id == framework_id,
                Framework.urn == framework_id
            )
        ).first()
        
        if not framework:
            return jsonify({'error': 'Framework not found'}), 404
        
        tree = framework.get_tree()
        return jsonify({
            'framework': framework.to_dict(),
            'tree': tree
        }), 200
    
    
    @app.route('/api/frameworks/names/', methods=['GET'])
    def get_framework_names():
        """
        Get Framework Names (Translated)
        ---
        tags:
          - Frameworks
        summary: Get translated names for multiple frameworks
        description: Display framework names in user's language
        parameters:
          - name: id[]
            in: query
            type: array
            items:
              type: string
            description: Framework IDs
        responses:
          200:
            description: Dict mapping framework IDs to translated names
        """
        ids = request.args.getlist('id[]')
        if not ids:
            ids = request.args.getlist('id')
        
        if not ids:
            return jsonify({'error': 'No framework IDs provided'}), 400
        
        frameworks = Framework.query.filter(Framework.id.in_(ids)).all()
        
        names_dict = {}
        for framework in frameworks:
            names_dict[framework.id] = {
                'id': framework.id,
                'name': framework.name,
                'ref_id': framework.ref_id,
                'translations': framework.translations
            }
        
        return jsonify(names_dict), 200
    
    
    @app.route('/api/frameworks/used/', methods=['GET'])
    def get_used_frameworks():
        """
        Get Used Frameworks
        ---
        tags:
          - Frameworks
        summary: Get frameworks user has access to
        responses:
          200:
            description: Array of accessible frameworks
        """
        # For now, return all frameworks
        # In future, filter based on user permissions
        frameworks = Framework.query.all()
        return jsonify({
            'count': len(frameworks),
            'results': [f.to_dict() for f in frameworks]
        }), 200
    
    
    @app.route('/api/frameworks/', methods=['POST'])
    def create_framework():
        """
        Create Framework
        ---
        tags:
          - Frameworks
        summary: Create new framework
        parameters:
          - name: body
            in: body
            required: true
            schema:
              type: object
              properties:
                name:
                  type: string
                description:
                  type: string
                ref_id:
                  type: string
        responses:
          201:
            description: Framework created
        """
        data = request.get_json()
        
        urn = data.get('urn', f"urn:custom:framework:{data.get('ref_id')}")
        
        framework = Framework(
            id=urn,
            urn=urn,
            ref_id=data.get('ref_id'),
            name=data.get('name'),
            description=data.get('description'),
            min_score=data.get('min_score'),
            max_score=data.get('max_score'),
            scores_definition=data.get('scores_definition', []),
            translations=data.get('translations', {})
        )
        
        db.session.add(framework)
        db.session.commit()
        
        return jsonify(framework.to_dict()), 201
    
    
    @app.route('/api/frameworks/<path:framework_id>/', methods=['PUT', 'PATCH'])
    def update_framework(framework_id):
        """
        Update Framework
        ---
        tags:
          - Frameworks
        summary: Update framework details
        parameters:
          - name: framework_id
            in: path
            required: true
            type: string
          - name: body
            in: body
            required: true
            schema:
              type: object
        responses:
          200:
            description: Framework updated
        """
        framework = Framework.query.filter(
            db.or_(
                Framework.id == framework_id,
                Framework.urn == framework_id
            )
        ).first()
        
        if not framework:
            return jsonify({'error': 'Framework not found'}), 404
        
        data = request.get_json()
        
        if 'name' in data:
            framework.name = data['name']
        if 'description' in data:
            framework.description = data['description']
        if 'min_score' in data:
            framework.min_score = data['min_score']
        if 'max_score' in data:
            framework.max_score = data['max_score']
        if 'scores_definition' in data:
            framework.scores_definition = data['scores_definition']
        if 'translations' in data:
            framework.translations = data['translations']
        
        db.session.commit()
        
        return jsonify(framework.to_dict()), 200
    
    
    @app.route('/api/frameworks/<path:framework_id>/', methods=['DELETE'])
    def delete_framework(framework_id):
        """
        Delete Framework
        ---
        tags:
          - Frameworks
        summary: Delete framework from system
        parameters:
          - name: framework_id
            in: path
            required: true
            type: string
        responses:
          200:
            description: Framework deleted
        """
        framework = Framework.query.filter(
            db.or_(
                Framework.id == framework_id,
                Framework.urn == framework_id
            )
        ).first()
        
        if framework:
            db.session.delete(framework)
            db.session.commit()
        
        return jsonify({'status': 'success', 'message': 'Framework deleted'}), 200
    
    
    # ==================== REQUIREMENT NODES ====================
    
    @app.route('/api/requirement-nodes/', methods=['GET'])
    def list_requirement_nodes():
        """
        List Requirements
        ---
        tags:
          - Requirements
        summary: List all requirements across all frameworks
        parameters:
          - name: framework
            in: query
            type: string
            description: Filter by framework ID
          - name: ref_id
            in: query
            type: string
            description: Filter by ref_id
          - name: search
            in: query
            type: string
            description: Search in name and description
        responses:
          200:
            description: Array of requirements
        """
        query = RequirementNode.query
        
        if framework := request.args.get('framework'):
            query = query.filter_by(framework_id=framework)
        if ref_id := request.args.get('ref_id'):
            query = query.filter_by(ref_id=ref_id)
        if search := request.args.get('search'):
            query = query.filter(
                db.or_(
                    RequirementNode.name.ilike(f'%{search}%'),
                    RequirementNode.description.ilike(f'%{search}%')
                )
            )
        
        requirements = query.all()
        return jsonify({
            'count': len(requirements),
            'results': [req.to_dict() for req in requirements]
        }), 200
    
    
    @app.route('/api/requirement-nodes/<path:req_id>/', methods=['GET'])
    def get_requirement_node(req_id):
        """
        Get Requirement Details
        ---
        tags:
          - Requirements
        summary: Get single requirement with related controls
        parameters:
          - name: req_id
            in: path
            required: true
            type: string
        responses:
          200:
            description: Requirement object
        """
        requirement = RequirementNode.query.filter(
            db.or_(
                RequirementNode.id == req_id,
                RequirementNode.urn == req_id
            )
        ).first()
        
        if not requirement:
            return jsonify({'error': 'Requirement not found'}), 404
        
        return jsonify(requirement.to_dict(include_children=True)), 200
