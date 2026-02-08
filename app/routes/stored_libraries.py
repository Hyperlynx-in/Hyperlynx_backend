"""Library management routes"""
from flask import jsonify, request, current_app
from application import db
from app.models import StoredLibrary, LoadedLibrary, Framework, RequirementNode, ReferenceControl, RiskMatrix, RequirementMappingSet, RequirementMapping
import yaml
import os
from pathlib import Path
from datetime import datetime


def register_library_routes(app):
    """Register all library-related API routes"""
    
    # ==================== STORED LIBRARIES (CATALOG) ====================
    
    @app.route('/api/stored-libraries/', methods=['GET'])
    def list_stored_libraries():
        """
        List Available Libraries in Catalog
        ---
        tags:
          - Stored Libraries
        summary: List all libraries in catalog
        description: Get all libraries available (not yet loaded). Supports filtering and search.
        parameters:
          - name: urn
            in: query
            type: string
            description: Filter by URN
          - name: locale
            in: query
            type: string
            description: Filter by locale (en, fr, de, etc.)
          - name: version
            in: query
            type: string
            description: Filter by version
          - name: provider
            in: query
            type: string
            description: Filter by provider
          - name: object_type
            in: query
            type: string
            description: Filter by object type (framework, reference_controls, risk_matrix)
          - name: search
            in: query
            type: string
            description: Search in name and description
          - name: is_loaded
            in: query
            type: boolean
            description: Filter by loaded status
          - name: limit
            in: query
            type: integer
            default: 20
            description: Number of results to return
          - name: offset
            in: query
            type: integer
            default: 0
            description: Offset for pagination
        responses:
          200:
            description: List of stored libraries
        """
        query = StoredLibrary.query
        
        # Filters
        if urn := request.args.get('urn'):
            query = query.filter(StoredLibrary.urn.ilike(f'%{urn}%'))
        if locale := request.args.get('locale'):
            query = query.filter_by(locale=locale)
        if version := request.args.get('version'):
            query = query.filter_by(version=version)
        if provider := request.args.get('provider'):
            query = query.filter_by(provider=provider)
        if object_type := request.args.get('object_type'):
            query = query.filter_by(object_type=object_type)
        if request.args.get('is_loaded') is not None:
            is_loaded = request.args.get('is_loaded').lower() == 'true'
            query = query.filter_by(is_loaded=is_loaded)
        
        # Search
        if search := request.args.get('search'):
            query = query.filter(
                db.or_(
                    StoredLibrary.name.ilike(f'%{search}%'),
                    StoredLibrary.description.ilike(f'%{search}%'),
                    StoredLibrary.ref_id.ilike(f'%{search}%')
                )
            )
        
        # Pagination
        limit = int(request.args.get('limit', 20))
        offset = int(request.args.get('offset', 0))
        
        total = query.count()
        libraries = query.limit(limit).offset(offset).all()
        
        return jsonify({
            'count': total,
            'results': [lib.to_dict() for lib in libraries]
        }), 200
    
    
    @app.route('/api/stored-libraries/<path:library_id>/', methods=['GET'])
    def get_stored_library(library_id):
        """
        Get Library Metadata
        ---
        tags:
          - Stored Libraries
        summary: Get library metadata by URN or ID
        parameters:
          - name: library_id
            in: path
            required: true
            type: string
            description: Library URN or ID
        responses:
          200:
            description: Library metadata
          404:
            description: Library not found
        """
        library = StoredLibrary.query.filter(
            db.or_(
                StoredLibrary.id == library_id,
                StoredLibrary.urn == library_id
            )
        ).first()
        
        if not library:
            return jsonify({'error': 'Library not found'}), 404
        
        return jsonify(library.to_dict()), 200
    
    
    @app.route('/api/stored-libraries/<path:library_id>/content/', methods=['GET'])
    def get_stored_library_content(library_id):
        """
        Get Library Full Content
        ---
        tags:
          - Stored Libraries
        summary: Get full YAML content of library
        parameters:
          - name: library_id
            in: path
            required: true
            type: string
        responses:
          200:
            description: Library content with all objects
        """
        library = StoredLibrary.query.filter(
            db.or_(
                StoredLibrary.id == library_id,
                StoredLibrary.urn == library_id
            )
        ).first()
        
        if not library:
            return jsonify({'error': 'Library not found'}), 404
        
        return jsonify(library.to_dict(include_content=True)), 200
    
    
    @app.route('/api/stored-libraries/<path:library_id>/tree/', methods=['GET'])
    def get_stored_library_tree(library_id):
        """
        Get Library Tree (Framework View)
        ---
        tags:
          - Stored Libraries
        summary: Get framework requirements in tree structure
        parameters:
          - name: library_id
            in: path
            required: true
            type: string
        responses:
          200:
            description: Nested requirement hierarchy
        """
        library = StoredLibrary.query.filter(
            db.or_(
                StoredLibrary.id == library_id,
                StoredLibrary.urn == library_id
            )
        ).first()
        
        if not library:
            return jsonify({'error': 'Library not found'}), 404
        
        if not library.content or 'objects' not in library.content:
            return jsonify({'tree': []}), 200
        
        # Extract requirement nodes and build tree
        objects = library.content.get('objects', {})
        if 'framework' in objects:
            nodes = objects['framework'].get('requirement_nodes', [])
            # Build hierarchy
            tree = build_requirement_tree(nodes)
            return jsonify({'tree': tree}), 200
        
        return jsonify({'tree': []}), 200
    
    
    @app.route('/api/stored-libraries/<path:library_id>/import/', methods=['POST'])
    def import_stored_library(library_id):
        """
        Import/Load Library
        ---
        tags:
          - Stored Libraries
        summary: Load library into system (make it active)
        parameters:
          - name: library_id
            in: path
            required: true
            type: string
        responses:
          200:
            description: Library loaded successfully
          400:
            description: Library already loaded
          404:
            description: Library not found
        """
        library = StoredLibrary.query.filter(
            db.or_(
                StoredLibrary.id == library_id,
                StoredLibrary.urn == library_id
            )
        ).first()
        
        if not library:
            return jsonify({'error': 'Library not found'}), 404
        
        if library.is_loaded:
            return jsonify({'error': 'Library already loaded'}), 400
        
        # Create loaded library instance FIRST (before importing objects that reference it)
        loaded = LoadedLibrary(
            id=library.urn,
            urn=library.urn,
            stored_library_id=library.id,
            ref_id=library.ref_id,
            locale=library.locale,
            name=library.name,
            version=library.version,
            provider=library.provider
        )
        db.session.add(loaded)
        library.is_loaded = True
        db.session.flush()  # Flush to DB so foreign keys work
        
        # Now parse and import objects from library content
        if library.content and 'objects' in library.content:
            objects = library.content['objects']
            
            # Import frameworks
            if 'framework' in objects:
                import_framework_from_library(objects['framework'], library.urn)
            
            # Import reference controls
            if 'reference_controls' in objects:
                import_reference_controls(objects['reference_controls'], library.urn)
            
            # Import risk matrices
            if 'risk_matrix' in objects:
                import_risk_matrices(objects['risk_matrix'], library.urn)
            
            # Import mapping sets
            if 'requirement_mapping_sets' in objects:
                import_mapping_sets(objects['requirement_mapping_sets'], library.urn)
        
        # Commit everything
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Library loaded successfully',
            'library': loaded.to_dict()
        }), 200
    
    
    @app.route('/api/stored-libraries/<path:library_id>/unload/', methods=['POST'])
    def unload_stored_library(library_id):
        """
        Unload Library
        ---
        tags:
          - Stored Libraries
        summary: Deactivate loaded library
        parameters:
          - name: library_id
            in: path
            required: true
            type: string
        responses:
          200:
            description: Library unloaded
        """
        library = StoredLibrary.query.filter(
            db.or_(
                StoredLibrary.id == library_id,
                StoredLibrary.urn == library_id
            )
        ).first()
        
        if library:
            library.is_loaded = False
            LoadedLibrary.query.filter_by(urn=library.urn).delete()
            db.session.commit()
        
        return jsonify({'status': 'success', 'message': 'Library unloaded'}), 200
    
    
    @app.route('/api/stored-libraries/upload/', methods=['POST'])
    def upload_library():
        """
        Upload Custom Library
        ---
        tags:
          - Stored Libraries
        summary: Upload custom YAML library file
        consumes:
          - multipart/form-data
        parameters:
          - name: file
            in: formData
            type: file
            required: true
            description: YAML library file
        responses:
          201:
            description: Library uploaded
          400:
            description: Invalid file or format
        """
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if not file.filename.endswith(('.yaml', '.yml')):
            return jsonify({'error': 'Only YAML files allowed'}), 400
        
        try:
            content = yaml.safe_load(file.read())
            library = create_stored_library_from_yaml(content)
            db.session.add(library)
            db.session.commit()
            
            return jsonify({
                'status': 'success',
                'message': 'Library uploaded',
                'library': library.to_dict()
            }), 201
        except Exception as e:
            return jsonify({'error': f'Failed to parse YAML: {str(e)}'}), 400
    
    
    @app.route('/api/stored-libraries/provider/', methods=['GET'])
    def get_library_providers():
        """
        Get Library Providers
        ---
        tags:
          - Stored Libraries
        summary: Get list of all library providers
        responses:
          200:
            description: Dict of provider names
        """
        providers = db.session.query(StoredLibrary.provider).distinct().all()
        return jsonify({
            'providers': [p[0] for p in providers if p[0]]
        }), 200
    
    
    @app.route('/api/stored-libraries/locale/', methods=['GET'])
    def get_library_locales():
        """
        Get Available Locales
        ---
        tags:
          - Stored Libraries
        summary: Get all available language/locale codes
        responses:
          200:
            description: List of locales
        """
        locales = db.session.query(StoredLibrary.locale).distinct().all()
        return jsonify({
            'locales': [l[0] for l in locales if l[0]]
        }), 200
    
    
    @app.route('/api/stored-libraries/object_type/', methods=['GET'])
    def get_library_object_types():
        """
        Get Object Types
        ---
        tags:
          - Stored Libraries
        summary: Get all object types in libraries
        responses:
          200:
            description: List of types
        """
        types = db.session.query(StoredLibrary.object_type).distinct().all()
        return jsonify({
            'object_types': [t[0] for t in types if t[0]]
        }), 200
    
    
    @app.route('/api/stored-libraries/<path:library_id>/', methods=['DELETE'])
    def delete_stored_library(library_id):
        """
        Delete Library
        ---
        tags:
          - Stored Libraries
        summary: Delete library from catalog
        parameters:
          - name: library_id
            in: path
            required: true
            type: string
        responses:
          200:
            description: Library deleted
        """
        library = StoredLibrary.query.filter(
            db.or_(
                StoredLibrary.id == library_id,
                StoredLibrary.urn == library_id
            )
        ).first()
        
        if library:
            db.session.delete(library)
            db.session.commit()
        
        return jsonify({'status': 'success', 'message': 'Library deleted'}), 200


# ==================== HELPER FUNCTIONS ====================

def build_requirement_tree(nodes):
    """Build hierarchical tree from flat requirement list"""
    # Create lookup dict
    node_dict = {node.get('urn'): node for node in nodes if isinstance(node, dict)}
    
    # Find roots and build tree
    roots = []
    for node in nodes:
        if isinstance(node, dict):
            parent_urn = node.get('parent_urn')
            if not parent_urn:
                roots.append(node)
            else:
                if parent_urn in node_dict:
                    if 'children' not in node_dict[parent_urn]:
                        node_dict[parent_urn]['children'] = []
                    node_dict[parent_urn]['children'].append(node)
    
    return roots


def create_stored_library_from_yaml(content):
    """Create StoredLibrary model from YAML content"""
    urn = content.get('urn', '')
    
    # Determine object type
    object_type = 'mixed'
    if 'objects' in content:
        objects = content['objects']
        if 'framework' in objects:
            object_type = 'framework'
        elif 'reference_controls' in objects:
            object_type = 'reference_controls'
        elif 'risk_matrix' in objects:
            object_type = 'risk_matrix'
        elif 'requirement_mapping_sets' in objects:
            object_type = 'mapping'
    
    library = StoredLibrary(
        id=urn,
        urn=urn,
        ref_id=content.get('ref_id', ''),
        locale=content.get('locale', 'en'),
        name=content.get('name', ''),
        description=content.get('description', ''),
        copyright=content.get('copyright', ''),
        version=str(content.get('version', '1')),
        provider=content.get('provider', ''),
        packager=content.get('packager', ''),
        object_type=object_type,
        content=content,
        translations=content.get('translations', {})
    )
    
    # Parse publication date
    if pub_date := content.get('publication_date'):
        try:
            library.publication_date = datetime.strptime(pub_date, '%Y-%m-%d').date()
        except:
            pass
    
    return library


def import_framework_from_library(framework_data, library_urn):
    """Import framework and requirements from library"""
    urn = framework_data.get('urn')
    
    # Create framework
    framework = Framework(
        id=urn,
        urn=urn,
        ref_id=framework_data.get('ref_id', ''),
        name=framework_data.get('name', ''),
        description=framework_data.get('description', ''),
        library_urn=library_urn,
        min_score=framework_data.get('min_score'),
        max_score=framework_data.get('max_score'),
        scores_definition=framework_data.get('scores_definition', []),
        translations=framework_data.get('translations', {})
    )
    db.session.add(framework)
    
    # Import requirements
    if 'requirement_nodes' in framework_data:
        for req_data in framework_data['requirement_nodes']:
            req = RequirementNode(
                id=req_data.get('urn'),
                urn=req_data.get('urn'),
                ref_id=req_data.get('ref_id'),
                name=req_data.get('name'),
                description=req_data.get('description'),
                framework_id=urn,
                parent_urn=req_data.get('parent_urn'),
                order_id=req_data.get('order_id', 0),
                assessable=req_data.get('assessable', True),
                translations=req_data.get('translations', {})
            )
            db.session.add(req)
    
    db.session.flush()


def import_reference_controls(controls_data, library_urn):
    """Import reference controls from library"""
    for control_data in controls_data:
        control = ReferenceControl(
            id=control_data.get('urn'),
            urn=control_data.get('urn'),
            ref_id=control_data.get('ref_id'),
            name=control_data.get('name'),
            description=control_data.get('description'),
            library_urn=library_urn,
            category=control_data.get('category'),
            csf_function=control_data.get('csf_function'),
            annotation=control_data.get('annotation'),
            typical_evidence=control_data.get('typical_evidence'),
            translations=control_data.get('translations', {})
        )
        db.session.add(control)
    
    db.session.flush()


def import_risk_matrices(matrices_data, library_urn):
    """Import risk matrices from library"""
    for matrix_data in matrices_data:
        matrix = RiskMatrix(
            id=matrix_data.get('urn'),
            urn=matrix_data.get('urn'),
            ref_id=matrix_data.get('ref_id'),
            name=matrix_data.get('name'),
            description=matrix_data.get('description'),
            library_urn=library_urn,
            probability=matrix_data.get('probability', []),
            impact=matrix_data.get('impact', []),
            grid=matrix_data.get('grid', []),
            translations=matrix_data.get('translations', {})
        )
        db.session.add(matrix)
    
    db.session.flush()


def import_mapping_sets(mappings_data, library_urn):
    """Import requirement mapping sets from library"""
    for mapping_data in mappings_data:
        mapping_set = RequirementMappingSet(
            id=mapping_data.get('urn'),
            urn=mapping_data.get('urn'),
            ref_id=mapping_data.get('ref_id'),
            name=mapping_data.get('name'),
            description=mapping_data.get('description'),
            library_urn=library_urn,
            source_framework_urn=mapping_data.get('source_framework_urn'),
            target_framework_urn=mapping_data.get('target_framework_urn'),
            translations=mapping_data.get('translations', {})
        )
        db.session.add(mapping_set)
        
        # Import individual mappings
        if 'mappings' in mapping_data:
            for map_item in mapping_data['mappings']:
                mapping = RequirementMapping(
                    id=f"{mapping_set.urn}:{map_item.get('source')}:{map_item.get('target')}",
                    mapping_set_id=mapping_set.id,
                    source_requirement_urn=map_item.get('source'),
                    target_requirement_urn=map_item.get('target'),
                    relationship_type=map_item.get('relationship', 'related'),
                    rationale=map_item.get('rationale')
                )
                db.session.add(mapping)
    
    db.session.flush()
