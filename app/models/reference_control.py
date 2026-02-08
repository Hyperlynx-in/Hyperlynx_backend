"""Reference control/measure models"""
from application import db
from datetime import datetime


class ReferenceControl(db.Model):
    """Reference controls/measures (security controls catalog)"""
    __tablename__ = 'reference_controls'
    
    id = db.Column(db.String(255), primary_key=True)
    urn = db.Column(db.String(255), unique=True, index=True)
    ref_id = db.Column(db.String(100))
    name = db.Column(db.String(500), nullable=False)
    description = db.Column(db.Text)
    
    library_urn = db.Column(db.String(255), db.ForeignKey('loaded_libraries.urn'))
    
    category = db.Column(db.String(100))  # policy, process, technical, organizational
    csf_function = db.Column(db.String(50))  # govern, identify, protect, detect, respond, recover
    
    # Additional metadata
    annotation = db.Column(db.Text)
    typical_evidence = db.Column(db.Text)
    implementation_guidance = db.Column(db.Text)
    
    translations = db.Column(db.JSON)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    library = db.relationship('LoadedLibrary', backref='reference_controls')
    
    def to_dict(self):
        return {
            'id': self.id,
            'urn': self.urn,
            'ref_id': self.ref_id,
            'name': self.name,
            'description': self.description,
            'library_urn': self.library_urn,
            'category': self.category,
            'csf_function': self.csf_function,
            'annotation': self.annotation,
            'typical_evidence': self.typical_evidence,
            'implementation_guidance': self.implementation_guidance,
            'translations': self.translations,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
