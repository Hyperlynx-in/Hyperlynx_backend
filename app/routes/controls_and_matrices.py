"""Reference controls and risk matrices routes"""
from flask import jsonify, request
from typing import Any, Dict
from application import db
from app.models import ReferenceControl, RiskMatrix


def register_control_routes(app):
    """Register reference control routes"""
    
    @app.route('/api/reference-controls/', methods=['GET'])
    def list_reference_controls():
        """
        List Reference Controls
        ---
        tags:
          - Reference Controls
        parameters:
          - in: query
            name: category
            type: string
            description: Filter by category
          - in: query
            name: library
            type: string
            description: Filter by library URN
          - in: query
            name: search
            type: string
            description: Search term for name or description
          - in: query
            name: limit
            type: integer
            default: 100
          - in: query
            name: offset
            type: integer
            default: 0
        responses:
          200:
            description: A list of reference controls
        """
        query = ReferenceControl.query
        
        if category := request.args.get('category'):
            query = query.filter_by(category=category)
        if library := request.args.get('library'):
            query = query.filter(ReferenceControl.library_urn.ilike(f'%{library}%'))
        if search := request.args.get('search'):
            query = query.filter(
                db.or_(
                    ReferenceControl.name.ilike(f'%{search}%'),
                    ReferenceControl.description.ilike(f'%{search}%')
                )
            )
        
        limit = int(request.args.get('limit', 100))
        offset = int(request.args.get('offset', 0))
        
        total = query.count()
        controls = query.limit(limit).offset(offset).all()
        
        return jsonify({'count': total, 'results': [c.to_dict() for c in controls]}), 200
    
    
    @app.route('/api/reference-controls/<path:control_id>/', methods=['GET'])
    def get_reference_control(control_id):
        """
        Get Control Details
        ---
        tags:
          - Reference Controls
        parameters:
          - in: path
            name: control_id
            required: true
            type: string
        responses:
          200:
            description: Reference control details
          404:
            description: Control not found
        """
        control = ReferenceControl.query.filter(
            db.or_(ReferenceControl.id == control_id, ReferenceControl.urn == control_id)
        ).first()
        
        if not control:
            return jsonify({'error': 'Control not found'}), 404
        
        return jsonify(control.to_dict()), 200
    
    
    @app.route('/api/reference-controls/', methods=['POST'])
    def create_reference_control():
        """
        Create Reference Control
        ---
        tags:
          - Reference Controls
        consumes:
          - application/json
        parameters:
          - in: body
            name: body
            required: true
            schema:
              type: object
              properties:
                ref_id:
                  type: string
                name:
                  type: string
                description:
                  type: string
                category:
                  type: string
                csf_function:
                  type: string
                urn:
                  type: string
        responses:
          201:
            description: Control created
        """
        data: Dict[str, Any] = request.get_json() or {}
        urn = data.get('urn', f"urn:custom:control:{data.get('ref_id')}")
        
        control = ReferenceControl()
        control.id = urn
        control.urn = urn
        control.ref_id = data.get('ref_id')
        control.name = data.get('name')
        control.description = data.get('description')
        control.category = data.get('category')
        control.csf_function = data.get('csf_function')
        
        db.session.add(control)
        db.session.commit()
        
        return jsonify(control.to_dict()), 201
    
    
    @app.route('/api/reference-controls/<path:control_id>/', methods=['PUT', 'PATCH'])
    def update_reference_control(control_id):
        """
        Update Reference Control
        ---
        tags:
          - Reference Controls
        parameters:
          - in: path
            name: control_id
            required: true
            type: string
          - in: body
            name: body
            schema:
              type: object
        responses:
          200:
            description: Control updated
          404:
            description: Control not found
        """
        control = ReferenceControl.query.filter(
            db.or_(ReferenceControl.id == control_id, ReferenceControl.urn == control_id)
        ).first()
        
        if not control:
            return jsonify({'error': 'Control not found'}), 404
        
        data: Dict[str, Any] = request.get_json() or {}
        for key in ['name', 'description', 'category', 'csf_function', 'annotation']:
            if key in data:
                setattr(control, key, data[key])
        
        db.session.commit()
        return jsonify(control.to_dict()), 200
    
    
    @app.route('/api/reference-controls/<path:control_id>/', methods=['DELETE'])
    def delete_reference_control(control_id):
        """
        Delete Reference Control
        ---
        tags:
          - Reference Controls
        parameters:
          - in: path
            name: control_id
            required: true
            type: string
        responses:
          200:
            description: Control deleted successfully
        """
        control = ReferenceControl.query.filter(
            db.or_(ReferenceControl.id == control_id, ReferenceControl.urn == control_id)
        ).first()
        
        if control:
            db.session.delete(control)
            db.session.commit()
        
        return jsonify({'status': 'success'}), 200


def register_risk_matrix_routes(app):
    """Register risk matrix routes"""
    
    @app.route('/api/risk-matrices/', methods=['GET'])
    def list_risk_matrices():
        """
        List Risk Matrices
        ---
        tags:
          - Risk Matrices
        responses:
          200:
            description: A list of risk matrices
        """
        matrices = RiskMatrix.query.all()
        return jsonify({'count': len(matrices), 'results': [m.to_dict() for m in matrices]}), 200
    
    
    @app.route('/api/risk-matrices/<path:matrix_id>/', methods=['GET'])
    def get_risk_matrix(matrix_id):
        """
        Get Risk Matrix Details
        ---
        tags:
          - Risk Matrices
        parameters:
          - in: path
            name: matrix_id
            required: true
            type: string
        responses:
          200:
            description: Risk matrix details
          404:
            description: Matrix not found
        """
        matrix = RiskMatrix.query.filter(
            db.or_(RiskMatrix.id == matrix_id, RiskMatrix.urn == matrix_id)
        ).first()
        
        if not matrix:
            return jsonify({'error': 'Risk matrix not found'}), 404
        
        return jsonify(matrix.to_dict()), 200
    
    
    @app.route('/api/risk-matrices/', methods=['POST'])
    def create_risk_matrix():
        """
        Create Risk Matrix
        ---
        tags:
          - Risk Matrices
        consumes:
          - application/json
        parameters:
          - in: body
            name: body
            required: true
            schema:
              type: object
        responses:
          201:
            description: Matrix created
        """
        data: Dict[str, Any] = request.get_json() or {}
        urn = data.get('urn', f"urn:custom:matrix:{data.get('ref_id')}")
        
        # FIX: Instantiate first, then assign properties to satisfy Pylance
        matrix = RiskMatrix()
        matrix.id = urn
        matrix.urn = urn
        matrix.ref_id = data.get('ref_id')
        matrix.name = data.get('name')
        matrix.description = data.get('description')
        matrix.probability = data.get('probability', [])
        matrix.impact = data.get('impact', [])
        matrix.grid = data.get('grid', [])
        
        db.session.add(matrix)
        db.session.commit()
        
        return jsonify(matrix.to_dict()), 201
    
    
    @app.route('/api/risk-matrices/<path:matrix_id>/', methods=['PUT', 'PATCH'])
    def update_risk_matrix(matrix_id):
        """
        Update Risk Matrix
        ---
        tags:
          - Risk Matrices
        parameters:
          - in: path
            name: matrix_id
            required: true
            type: string
          - in: body
            name: body
            schema:
              type: object
        responses:
          200:
            description: Matrix updated
          404:
            description: Matrix not found
        """
        matrix = RiskMatrix.query.filter(
            db.or_(RiskMatrix.id == matrix_id, RiskMatrix.urn == matrix_id)
        ).first()
        
        if not matrix:
            return jsonify({'error': 'Risk matrix not found'}), 404
        
        data: Dict[str, Any] = request.get_json() or {}
        for key in ['name', 'description', 'probability', 'impact', 'grid']:
            if key in data:
                setattr(matrix, key, data[key])
        
        db.session.commit()
        return jsonify(matrix.to_dict()), 200
    
    
    @app.route('/api/risk-matrices/<path:matrix_id>/', methods=['DELETE'])
    def delete_risk_matrix(matrix_id):
        """
        Delete Risk Matrix
        ---
        tags:
          - Risk Matrices
        parameters:
          - in: path
            name: matrix_id
            required: true
            type: string
        responses:
          200:
            description: Matrix deleted successfully
        """
        matrix = RiskMatrix.query.filter(
            db.or_(RiskMatrix.id == matrix_id, RiskMatrix.urn == matrix_id)
        ).first()
        
        if matrix:
            db.session.delete(matrix)
            db.session.commit()
        
        return jsonify({'status': 'success'}), 200