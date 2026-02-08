"""Loaded libraries routes"""
from flask import jsonify, request
from application import db
from app.models import LoadedLibrary, Framework, ReferenceControl, RiskMatrix, RequirementMappingSet


def register_loaded_library_routes(app):
    """Register loaded library API routes"""
    
    @app.route('/api/loaded-libraries/', methods=['GET'])
    def list_loaded_libraries():
        """
        List Loaded Libraries
        ---
        tags:
          - Loaded Libraries
        summary: List all currently active/imported libraries
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
        responses:
          200:
            description: Array of loaded library metadata
        """
        query = LoadedLibrary.query
        
        if urn := request.args.get('urn'):
            query = query.filter(LoadedLibrary.urn.ilike(f'%{urn}%'))
        if locale := request.args.get('locale'):
            query = query.filter_by(locale=locale)
        if version := request.args.get('version'):
            query = query.filter_by(version=version)
        
        libraries = query.all()
        return jsonify({
            'count': len(libraries),
            'results': [lib.to_dict() for lib in libraries]
        }), 200
    
    
    @app.route('/api/loaded-libraries/<path:library_urn>/', methods=['GET'])
    def get_loaded_library(library_urn):
        """
        Get Loaded Library Details
        ---
        tags:
          - Loaded Libraries
        summary: Get loaded library full details
        parameters:
          - name: library_urn
            in: path
            required: true
            type: string
        responses:
          200:
            description: Library object with all objects
        """
        library = LoadedLibrary.query.filter_by(urn=library_urn).first()
        if not library:
            return jsonify({'error': 'Loaded library not found'}), 404
        
        return jsonify(library.to_dict()), 200
    
    
    @app.route('/api/loaded-libraries/<path:library_urn>/content/', methods=['GET'])
    def get_loaded_library_content(library_urn):
        """
        Get Loaded Library Content
        ---
        tags:
          - Loaded Libraries
        summary: Get all objects in loaded library
        parameters:
          - name: library_urn
            in: path
            required: true
            type: string
        responses:
          200:
            description: Dict with frameworks, controls, matrices, mappings
        """
        library = LoadedLibrary.query.filter_by(urn=library_urn).first()
        if not library:
            return jsonify({'error': 'Loaded library not found'}), 404
        
        # Get all objects from this library
        frameworks = Framework.query.filter_by(library_urn=library_urn).all()
        controls = ReferenceControl.query.filter_by(library_urn=library_urn).all()
        matrices = RiskMatrix.query.filter_by(library_urn=library_urn).all()
        mappings = RequirementMappingSet.query.filter_by(library_urn=library_urn).all()
        
        return jsonify({
            'library': library.to_dict(),
            'frameworks': [f.to_dict() for f in frameworks],
            'reference_controls': [c.to_dict() for c in controls],
            'risk_matrices': [m.to_dict() for m in matrices],
            'requirement_mapping_sets': [ms.to_dict() for ms in mappings]
        }), 200
    
    
    @app.route('/api/loaded-libraries/<path:library_urn>/tree/', methods=['GET'])
    def get_loaded_library_tree(library_urn):
        """
        Get Loaded Library Tree
        ---
        tags:
          - Loaded Libraries
        summary: Get framework requirements tree
        parameters:
          - name: library_urn
            in: path
            required: true
            type: string
        responses:
          200:
            description: Nested requirement structure
        """
        library = LoadedLibrary.query.filter_by(urn=library_urn).first()
        if not library:
            return jsonify({'error': 'Loaded library not found'}), 404
        
        # Get framework from this library
        framework = Framework.query.filter_by(library_urn=library_urn).first()
        if not framework:
            return jsonify({'tree': []}), 200
        
        tree = framework.get_tree()
        return jsonify({'tree': tree}), 200
    
    
    @app.route('/api/loaded-libraries/<path:library_urn>/', methods=['DELETE'])
    def unload_library(library_urn):
        """
        Unload/Delete Loaded Library
        ---
        tags:
          - Loaded Libraries
        summary: Unload library from system
        parameters:
          - name: library_urn
            in: path
            required: true
            type: string
        responses:
          200:
            description: Library unloaded
        """
        library = LoadedLibrary.query.filter_by(urn=library_urn).first()
        if library:
            # Also update stored library
            if library.stored_library:
                library.stored_library.is_loaded = False
            
            # Delete loaded library (cascades will handle related objects)
            db.session.delete(library)
            db.session.commit()
        
        return jsonify({'status': 'success', 'message': 'Library unloaded'}), 200
