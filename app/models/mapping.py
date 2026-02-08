"""Requirement mapping models (framework crosswalks)"""
from application import db
from datetime import datetime


class RequirementMappingSet(db.Model):
    """Set of mappings between two frameworks"""
    __tablename__ = 'requirement_mapping_sets'
    
    id = db.Column(db.String(255), primary_key=True)
    urn = db.Column(db.String(255), unique=True, index=True)
    ref_id = db.Column(db.String(100))
    name = db.Column(db.String(500), nullable=False)
    description = db.Column(db.Text)
    
    library_urn = db.Column(db.String(255), db.ForeignKey('loaded_libraries.urn'))
    
    source_framework_urn = db.Column(db.String(255))
    target_framework_urn = db.Column(db.String(255))
    
    translations = db.Column(db.JSON)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    library = db.relationship('LoadedLibrary', backref='mapping_sets')
    mappings = db.relationship('RequirementMapping', backref='mapping_set', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self, include_mappings=False):
        data = {
            'id': self.id,
            'urn': self.urn,
            'ref_id': self.ref_id,
            'name': self.name,
            'description': self.description,
            'library_urn': self.library_urn,
            'source_framework_urn': self.source_framework_urn,
            'target_framework_urn': self.target_framework_urn,
            'translations': self.translations,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_mappings:
            data['mappings'] = [m.to_dict() for m in self.mappings]
            
        return data


class RequirementMapping(db.Model):
    """Individual requirement-to-requirement mapping"""
    __tablename__ = 'requirement_mappings'
    
    id = db.Column(db.String(255), primary_key=True)
    mapping_set_id = db.Column(db.String(255), db.ForeignKey('requirement_mapping_sets.id'), nullable=False)
    
    source_requirement_urn = db.Column(db.String(255))
    target_requirement_urn = db.Column(db.String(255))
    
    relationship_type = db.Column(db.String(50))  # equal, subset, superset, related, similar
    strength = db.Column(db.Integer)  # 0-100 mapping confidence
    
    rationale = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'mapping_set_id': self.mapping_set_id,
            'source_requirement_urn': self.source_requirement_urn,
            'target_requirement_urn': self.target_requirement_urn,
            'relationship_type': self.relationship_type,
            'strength': self.strength,
            'rationale': self.rationale,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
