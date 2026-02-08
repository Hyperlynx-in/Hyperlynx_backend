"""Reference controls and risk matrices routes"""
from flask import jsonify, request
from application import db
from app.models import ReferenceControl, RiskMatrix


def register_control_routes(app):
    """Register reference control routes"""
    
    @app.route('/api/reference-controls/', methods=['GET'])
    def list_reference_controls():
        """List Controls --- tags: [Reference Controls]"""
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
        """Get Control Details --- tags: [Reference Controls]"""
        control = ReferenceControl.query.filter(
            db.or_(ReferenceControl.id == control_id, ReferenceControl.urn == control_id)
        ).first()
        
        if not control:
            return jsonify({'error': 'Control not found'}), 404
        
        return jsonify(control.to_dict()), 200
    
    
    @app.route('/api/reference-controls/', methods=['POST'])
    def create_reference_control():
        """Create Control --- tags: [Reference Controls]"""
        data = request.get_json()
        urn = data.get('urn', f"urn:custom:control:{data.get('ref_id')}")
        
        control = ReferenceControl(
            id=urn, urn=urn,
            ref_id=data.get('ref_id'),
            name=data.get('name'),
            description=data.get('description'),
            category=data.get('category'),
            csf_function=data.get('csf_function')
        )
        
        db.session.add(control)
        db.session.commit()
        
        return jsonify(control.to_dict()), 201
    
    
    @app.route('/api/reference-controls/<path:control_id>/', methods=['PUT', 'PATCH'])
    def update_reference_control(control_id):
        """Update Control --- tags: [Reference Controls]"""
        control = ReferenceControl.query.filter(
            db.or_(ReferenceControl.id == control_id, ReferenceControl.urn == control_id)
        ).first()
        
        if not control:
            return jsonify({'error': 'Control not found'}), 404
        
        data = request.get_json()
        for key in ['name', 'description', 'category', 'csf_function', 'annotation']:
            if key in data:
                setattr(control, key, data[key])
        
        db.session.commit()
        return jsonify(control.to_dict()), 200
    
    
    @app.route('/api/reference-controls/<path:control_id>/', methods=['DELETE'])
    def delete_reference_control(control_id):
        """Delete Control --- tags: [Reference Controls]"""
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
        """List Risk Matrices --- tags: [Risk Matrices]"""
        matrices = RiskMatrix.query.all()
        return jsonify({'count': len(matrices), 'results': [m.to_dict() for m in matrices]}), 200
    
    
    @app.route('/api/risk-matrices/<path:matrix_id>/', methods=['GET'])
    def get_risk_matrix(matrix_id):
        """Get Risk Matrix Details --- tags: [Risk Matrices]"""
        matrix = RiskMatrix.query.filter(
            db.or_(RiskMatrix.id == matrix_id, RiskMatrix.urn == matrix_id)
        ).first()
        
        if not matrix:
            return jsonify({'error': 'Risk matrix not found'}), 404
        
        return jsonify(matrix.to_dict()), 200
    
    
    @app.route('/api/risk-matrices/', methods=['POST'])
    def create_risk_matrix():
        """Create Risk Matrix --- tags: [Risk Matrices]"""
        data = request.get_json()
        urn = data.get('urn', f"urn:custom:matrix:{data.get('ref_id')}")
        
        matrix = RiskMatrix(
            id=urn, urn=urn,
            ref_id=data.get('ref_id'),
            name=data.get('name'),
            description=data.get('description'),
            probability=data.get('probability', []),
            impact=data.get('impact', []),
            grid=data.get('grid', [])
        )
        
        db.session.add(matrix)
        db.session.commit()
        
        return jsonify(matrix.to_dict()), 201
    
    
    @app.route('/api/risk-matrices/<path:matrix_id>/', methods=['PUT', 'PATCH'])
    def update_risk_matrix(matrix_id):
        """Update Risk Matrix --- tags: [Risk Matrices]"""
        matrix = RiskMatrix.query.filter(
            db.or_(RiskMatrix.id == matrix_id, RiskMatrix.urn == matrix_id)
        ).first()
        
        if not matrix:
            return jsonify({'error': 'Risk matrix not found'}), 404
        
        data = request.get_json()
        for key in ['name', 'description', 'probability', 'impact', 'grid']:
            if key in data:
                setattr(matrix, key, data[key])
        
        db.session.commit()
        return jsonify(matrix.to_dict()), 200
    
    
    @app.route('/api/risk-matrices/<path:matrix_id>/', methods=['DELETE'])
    def delete_risk_matrix(matrix_id):
        """Delete Risk Matrix --- tags: [Risk Matrices]"""
        matrix = RiskMatrix.query.filter(
            db.or_(RiskMatrix.id == matrix_id, RiskMatrix.urn == matrix_id)
        ).first()
        
        if matrix:
            db.session.delete(matrix)
            db.session.commit()
        
        return jsonify({'status': 'success'}), 200
