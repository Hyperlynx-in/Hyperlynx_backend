"""Library models for framework library management"""
from application import db
from datetime import datetime
import json


class StoredLibrary(db.Model):
    """Catalog of available libraries (not yet loaded)"""
    __tablename__ = 'stored_libraries'
    
    id = db.Column(db.String(255), primary_key=True)  # URN
    urn = db.Column(db.String(255), unique=True, nullable=False, index=True)
    ref_id = db.Column(db.String(100), nullable=False)
    locale = db.Column(db.String(10), nullable=False, default='en')
    name = db.Column(db.String(500), nullable=False)
    description = db.Column(db.Text)
    copyright = db.Column(db.Text)
    version = db.Column(db.String(50))
    publication_date = db.Column(db.Date)
    provider = db.Column(db.String(200))
    packager = db.Column(db.String(200))
    is_loaded = db.Column(db.Boolean, default=False)
    is_published = db.Column(db.Boolean, default=True)
    object_type = db.Column(db.String(100))  # framework, reference_controls, risk_matrix, mapping
    
    # Full YAML content stored as JSON
    content = db.Column(db.JSON)
    translations = db.Column(db.JSON)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self, include_content=False):
        data = {
            'id': self.id,
            'urn': self.urn,
            'ref_id': self.ref_id,
            'locale': self.locale,
            'name': self.name,
            'description': self.description,
            'copyright': self.copyright,
            'version': self.version,
            'publication_date': self.publication_date.isoformat() if self.publication_date else None,
            'provider': self.provider,
            'packager': self.packager,
            'is_loaded': self.is_loaded,
            'is_published': self.is_published,
            'object_type': self.object_type,
            'translations': self.translations,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_content and self.content:
            data['content'] = self.content
            
        return data


class LoadedLibrary(db.Model):
    """Active/imported libraries currently in use"""
    __tablename__ = 'loaded_libraries'
    
    id = db.Column(db.String(255), primary_key=True)  # URN
    urn = db.Column(db.String(255), unique=True, nullable=False, index=True)
    stored_library_id = db.Column(db.String(255), db.ForeignKey('stored_libraries.id'))
    
    # Denormalized fields for quick access
    ref_id = db.Column(db.String(100))
    locale = db.Column(db.String(10))
    name = db.Column(db.String(500))
    version = db.Column(db.String(50))
    provider = db.Column(db.String(200))
    
    loaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    loaded_by = db.Column(db.String(255))  # user ID
    
    # Relationships
    stored_library = db.relationship('StoredLibrary', backref='loaded_instances')
    
    def to_dict(self):
        return {
            'id': self.id,
            'urn': self.urn,
            'ref_id': self.ref_id,
            'locale': self.locale,
            'name': self.name,
            'version': self.version,
            'provider': self.provider,
            'loaded_at': self.loaded_at.isoformat() if self.loaded_at else None,
            'loaded_by': self.loaded_by
        }
