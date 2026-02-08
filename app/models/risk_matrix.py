"""Risk matrix models"""
from application import db
from datetime import datetime


class RiskMatrix(db.Model):
    """Risk assessment matrices"""
    __tablename__ = 'risk_matrices'
    
    id = db.Column(db.String(255), primary_key=True)
    urn = db.Column(db.String(255), unique=True, index=True)
    ref_id = db.Column(db.String(100))
    name = db.Column(db.String(500), nullable=False)
    description = db.Column(db.Text)
    
    library_urn = db.Column(db.String(255), db.ForeignKey('loaded_libraries.urn'))
    
    # Matrix definition as JSON
    probability = db.Column(db.JSON)  # List of probability levels
    impact = db.Column(db.JSON)  # List of impact levels
    grid = db.Column(db.JSON)  # 2D grid mapping probability x impact to risk level
    risk_levels = db.Column(db.JSON)  # Risk level definitions with colors
    
    is_enabled = db.Column(db.Boolean, default=True)
    
    translations = db.Column(db.JSON)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    library = db.relationship('LoadedLibrary', backref='risk_matrices')
    
    def to_dict(self):
        return {
            'id': self.id,
            'urn': self.urn,
            'ref_id': self.ref_id,
            'name': self.name,
            'description': self.description,
            'library_urn': self.library_urn,
            'probability': self.probability,
            'impact': self.impact,
            'grid': self.grid,
            'risk_levels': self.risk_levels,
            'is_enabled': self.is_enabled,
            'translations': self.translations,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
