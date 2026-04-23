from application import db
from datetime import datetime
import uuid

class CompanyProfile(db.Model):
    __tablename__ = 'company_profiles'
    
    id = db.Column(db.String(255), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(255), db.ForeignKey('users.id'), nullable=False)
    
    company_name = db.Column(db.String(255), nullable=False)
    industry = db.Column(db.String(255))
    employee_count = db.Column(db.String(100)) 
    annual_revenue = db.Column(db.String(100))
    
    # Expanded Context Fields
    operating_regions = db.Column(db.JSON, default=list) 
    services_provided = db.Column(db.JSON, default=list)        # New: e.g., SaaS, MSP, Payment Gateway
    regulatory_authorities = db.Column(db.JSON, default=list)   # New: e.g., SEC, FCA, EBA, HHS
    tech_stack = db.Column(db.JSON, default=list)       
    data_processed = db.Column(db.JSON, default=list)    
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "company_name": self.company_name,
            "industry": self.industry,
            "employee_count": self.employee_count,
            "annual_revenue": self.annual_revenue,
            "operating_regions": self.operating_regions or [],
            "services_provided": self.services_provided or [],
            "regulatory_authorities": self.regulatory_authorities or [],
            "tech_stack": self.tech_stack or [],
            "data_processed": self.data_processed or []
        }