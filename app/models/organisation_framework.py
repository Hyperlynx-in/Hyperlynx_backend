# app/models/organisation_framework.py
from application import db
from datetime import datetime
import uuid

class OrganisationFramework(db.Model):
    __tablename__ = 'organisation_frameworks'
    
    id = db.Column(db.String(255), primary_key=True, default=lambda: str(uuid.uuid4()))
    profile_id = db.Column(db.String(255), db.ForeignKey('company_profiles.id'), nullable=False)
    framework_id = db.Column(db.String(255), db.ForeignKey('frameworks.id'), nullable=False) # Assumes you have a frameworks table from Phase 3.1
    
    # Context
    is_mandatory = db.Column(db.Boolean, default=False)
    rationale = db.Column(db.Text)
    status = db.Column(db.String(50), default="active") # active, paused, assessing
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "profile_id": self.profile_id,
            "framework_id": self.framework_id,
            "is_mandatory": self.is_mandatory,
            "rationale": self.rationale,
            "status": self.status
        }