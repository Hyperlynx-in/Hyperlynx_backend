"""Framework and requirement models"""
from application import db
from datetime import datetime


class Framework(db.Model):
    """Security/compliance frameworks"""
    __tablename__ = 'frameworks'
    
    id = db.Column(db.String(255), primary_key=True)
    urn = db.Column(db.String(255), unique=True, index=True)
    ref_id = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(500), nullable=False)
    description = db.Column(db.Text)
    
    library_urn = db.Column(db.String(255), db.ForeignKey('loaded_libraries.urn'))
    
    min_score = db.Column(db.Integer)
    max_score = db.Column(db.Integer)
    scores_definition = db.Column(db.JSON)
    
    translations = db.Column(db.JSON)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    library = db.relationship('LoadedLibrary', backref='frameworks')
    requirements = db.relationship('RequirementNode', backref='framework', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self, include_requirements=False):
        data = {
            'id': self.id,
            'urn': self.urn,
            'ref_id': self.ref_id,
            'name': self.name,
            'description': self.description,
            'library_urn': self.library_urn,
            'min_score': self.min_score,
            'max_score': self.max_score,
            'scores_definition': self.scores_definition,
            'translations': self.translations,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_requirements:
            data['requirements'] = [req.to_dict() for req in self.requirements]
            
        return data
    
    def get_tree(self):
        """Get hierarchical tree of requirements"""
        # Get root requirements (no parent)
        roots = RequirementNode.query.filter_by(
            framework_id=self.id,
            parent_urn=None
        ).order_by(RequirementNode.order_id).all()
        
        def build_tree(node):
            children = RequirementNode.query.filter_by(
                framework_id=self.id,
                parent_urn=node.urn
            ).order_by(RequirementNode.order_id).all()
            
            tree = node.to_dict()
            if children:
                tree['children'] = [build_tree(child) for child in children]
            return tree
        
        return [build_tree(root) for root in roots]


class RequirementNode(db.Model):
    """Individual requirements within frameworks"""
    __tablename__ = 'requirement_nodes'
    
    id = db.Column(db.String(255), primary_key=True)
    urn = db.Column(db.String(255), unique=True, index=True)
    ref_id = db.Column(db.String(100))
    name = db.Column(db.String(500))
    description = db.Column(db.Text)
    
    framework_id = db.Column(db.String(255), db.ForeignKey('frameworks.id'), nullable=False)
    parent_urn = db.Column(db.String(255))  # Store parent URN but don't enforce FK constraint
    
    order_id = db.Column(db.Integer, default=0)
    level = db.Column(db.Integer, default=0)
    
    # Assessment fields
    assessable = db.Column(db.Boolean, default=True)
    maturity = db.Column(db.Integer)
    
    translations = db.Column(db.JSON)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def get_parent(self):
        """Get parent requirement by URN"""
        if self.parent_urn:
            return RequirementNode.query.filter_by(urn=self.parent_urn).first()
        return None
    
    def get_children(self):
        """Get child requirements"""
        return RequirementNode.query.filter_by(parent_urn=self.urn).order_by(RequirementNode.order_id).all()
    
    def to_dict(self, include_children=False):
        data = {
            'id': self.id,
            'urn': self.urn,
            'ref_id': self.ref_id,
            'name': self.name,
            'description': self.description,
            'framework_id': self.framework_id,
            'parent_urn': self.parent_urn,
            'order_id': self.order_id,
            'level': self.level,
            'assessable': self.assessable,
            'maturity': self.maturity,
            'translations': self.translations,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        
        if include_children:
            children = self.get_children()
            data['children'] = [child.to_dict(include_children=True) for child in children]
            
        return data
