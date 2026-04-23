import uuid
from datetime import datetime
from application import db



class RiskProfile(db.Model):
    """
    1-to-1 mapping with CompanyProfile. Stores the organization's 
    risk appetite, tolerance, and their selected RiskMatrix (e.g., 4x4 or 5x5).
    """
    __tablename__ = 'risk_profiles'
    
    id = db.Column(db.String(255), primary_key=True, default=lambda: str(uuid.uuid4()))
    profile_id = db.Column(db.String(255), db.ForeignKey('company_profiles.id', ondelete='CASCADE'), nullable=False, unique=True)
    
    risk_matrix_id = db.Column(db.String(255), db.ForeignKey('risk_matrices.id', ondelete='SET NULL'), nullable=True)
    
    risk_appetite = db.Column(db.String(100), default="Moderate") 
    risk_tolerance = db.Column(db.Text) 
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "profile_id": self.profile_id,
            "risk_matrix_id": self.risk_matrix_id,
            "risk_appetite": self.risk_appetite,
            "risk_tolerance": self.risk_tolerance
        }



class MetricDefinition(db.Model):
    """
    Defines WHAT is being measured (The Rule). 
    Adapted from CISO Assistant's 'metrology/models.py'
    """
    __tablename__ = 'metric_definitions'
    
    id = db.Column(db.String(255), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(100))  # e.g., 'People', 'Process', 'Technology'
    
    unit = db.Column(db.String(50))       # e.g., '%', 'days', 'count'
    target_value = db.Column(db.Float)    # What is the goal? (e.g., 100% patched)
    operator = db.Column(db.String(10))   # e.g., '>=', '<=', '==' (How to evaluate the target)
    periodicity = db.Column(db.String(50))# e.g., 'monthly', 'quarterly'
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class MetricSample(db.Model):
    """
    Defines the ACTUAL MEASUREMENT over time. 
    Adapted from CISO Assistant's 'CustomMetricSample'.
    Allows us to draw time-series charts on the dashboard.
    """
    __tablename__ = 'metric_samples'
    
    id = db.Column(db.String(255), primary_key=True, default=lambda: str(uuid.uuid4()))
    profile_id = db.Column(db.String(255), db.ForeignKey('company_profiles.id', ondelete='CASCADE'), nullable=False)
    definition_id = db.Column(db.String(255), db.ForeignKey('metric_definitions.id', ondelete='CASCADE'), nullable=False)
    
    value = db.Column(db.Float, nullable=False)
    measured_at = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text) # e.g., "Dip in patching compliance due to holiday freeze"
    
    
class Risk(db.Model):
    __tablename__ = 'risks'
    id = db.Column(db.String(255), primary_key=True, default=lambda: str(uuid.uuid4()))
    profile_id = db.Column(db.String(255), db.ForeignKey('company_profiles.id', ondelete='CASCADE'), nullable=False)
    risk_id = db.Column(db.String(50))
    name = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(100))
    likelihood = db.Column(db.Integer, nullable=False)
    impact = db.Column(db.Integer, nullable=False)
    score = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(50), default='Open')
    owner = db.Column(db.String(100))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            "id": self.id,
            "risk_id": self.risk_id,
            "name": self.name,
            "category": self.category,
            "likelihood": self.likelihood,
            "impact": self.impact,
            "score": self.score,
            "status": self.status,
            "owner": self.owner
        }