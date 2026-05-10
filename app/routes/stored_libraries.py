"""Library management routes"""
from flask import Blueprint, jsonify, request, current_app
from typing import Dict, Any, Optional
from application import db
from app.models import (
    StoredLibrary, LoadedLibrary, Framework, RequirementNode, 
    ReferenceControl, RiskMatrix, RequirementMappingSet, RequirementMapping
)
import yaml
import os
from pathlib import Path
from datetime import datetime


def register_library_routes(app):
    """Register all library-related API routes"""
    
    
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
          - name: locale
            in: query
            type: string
          - name: version
            in: query
            type: string
          - name: provider
            in: query
            type: string
          - name: object_type
            in: query
            type: string
          - name: search
            in: query
            type: string
          - name: is_loaded
            in: query
            type: boolean
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
            
        # FIX: Safe check before calling .lower()
        is_loaded_param = request.args.get('is_loaded')
        if is_loaded_param is not None:
            is_loaded = is_loaded_param.lower() == 'true'
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
        
        # FIX: Instantiate first, then assign
        loaded = LoadedLibrary()
        loaded.id = library.urn
        loaded.urn = library.urn
        loaded.stored_library_id = library.id
        loaded.ref_id = library.ref_id
        loaded.locale = library.locale
        loaded.name = library.name
        loaded.version = library.version
        loaded.provider = library.provider
        
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
        
        # FIX: Safe check for filename and extension
        if not file or not file.filename or not file.filename.endswith(('.yaml', '.yml')):
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
    
    # FIX: Instantiate first, then assign properties
    library = StoredLibrary()
    library.id = urn
    library.urn = urn
    library.ref_id = content.get('ref_id', '')
    library.locale = content.get('locale', 'en')
    library.name = content.get('name', '')
    library.description = content.get('description', '')
    library.copyright = content.get('copyright', '')
    library.version = str(content.get('version', '1'))
    library.provider = content.get('provider', '')
    library.packager = content.get('packager', '')
    library.object_type = object_type
    library.content = content
    library.translations = content.get('translations', {})
    
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
    
    # FIX: Instantiate first, then assign properties
    framework = Framework()
    framework.id = urn
    framework.urn = urn
    framework.ref_id = framework_data.get('ref_id', '')
    framework.name = framework_data.get('name', '')
    framework.description = framework_data.get('description', '')
    framework.library_urn = library_urn
    framework.min_score = framework_data.get('min_score')
    framework.max_score = framework_data.get('max_score')
    framework.scores_definition = framework_data.get('scores_definition', [])
    framework.translations = framework_data.get('translations', {})
    
    db.session.add(framework)
    
    # Import requirements
    if 'requirement_nodes' in framework_data:
        for req_data in framework_data['requirement_nodes']:
            # FIX: Instantiate first, then assign properties
            req = RequirementNode()
            req.id = req_data.get('urn')
            req.urn = req_data.get('urn')
            req.ref_id = req_data.get('ref_id')
            req.name = req_data.get('name')
            req.description = req_data.get('description')
            req.framework_id = urn
            req.parent_urn = req_data.get('parent_urn')
            req.order_id = req_data.get('order_id', 0)
            req.assessable = req_data.get('assessable', True)
            req.translations = req_data.get('translations', {})
            
            db.session.add(req)
    
    db.session.flush()


def import_reference_controls(controls_data, library_urn):
    """Import reference controls from library"""
    for control_data in controls_data:
        # FIX: Instantiate first, then assign properties
        control = ReferenceControl()
        control.id = control_data.get('urn')
        control.urn = control_data.get('urn')
        control.ref_id = control_data.get('ref_id')
        control.name = control_data.get('name')
        control.description = control_data.get('description')
        control.library_urn = library_urn
        control.category = control_data.get('category')
        control.csf_function = control_data.get('csf_function')
        control.annotation = control_data.get('annotation')
        control.typical_evidence = control_data.get('typical_evidence')
        control.translations = control_data.get('translations', {})
        
        db.session.add(control)
    
    db.session.flush()


def import_risk_matrices(matrices_data, library_urn):
    """Import risk matrices from library"""
    for matrix_data in matrices_data:
        # FIX: Instantiate first, then assign properties
        matrix = RiskMatrix()
        matrix.id = matrix_data.get('urn')
        matrix.urn = matrix_data.get('urn')
        matrix.ref_id = matrix_data.get('ref_id')
        matrix.name = matrix_data.get('name')
        matrix.description = matrix_data.get('description')
        matrix.library_urn = library_urn
        matrix.probability = matrix_data.get('probability', [])
        matrix.impact = matrix_data.get('impact', [])
        matrix.grid = matrix_data.get('grid', [])
        matrix.translations = matrix_data.get('translations', {})
        
        db.session.add(matrix)
    
    db.session.flush()


def import_mapping_sets(mappings_data, library_urn):
    """Import requirement mapping sets from library"""
    for mapping_data in mappings_data:
        # FIX: Instantiate first, then assign properties
        mapping_set = RequirementMappingSet()
        mapping_set.id = mapping_data.get('urn')
        mapping_set.urn = mapping_data.get('urn')
        mapping_set.ref_id = mapping_data.get('ref_id')
        mapping_set.name = mapping_data.get('name')
        mapping_set.description = mapping_data.get('description')
        mapping_set.library_urn = library_urn
        mapping_set.source_framework_urn = mapping_data.get('source_framework_urn')
        mapping_set.target_framework_urn = mapping_data.get('target_framework_urn')
        mapping_set.translations = mapping_data.get('translations', {})
        
        db.session.add(mapping_set)
        
        # Import individual mappings
        if 'mappings' in mapping_data:
            for map_item in mapping_data['mappings']:
                # FIX: Instantiate first, then assign properties
                mapping = RequirementMapping()
                mapping.id = f"{mapping_set.urn}:{map_item.get('source')}:{map_item.get('target')}"
                mapping.mapping_set_id = mapping_set.id
                mapping.source_requirement_urn = map_item.get('source')
                mapping.target_requirement_urn = map_item.get('target')
                mapping.relationship_type = map_item.get('relationship', 'related')
                mapping.rationale = map_item.get('rationale')
                
                db.session.add(mapping)
    
    db.session.flush()