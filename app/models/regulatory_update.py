from application import db
from datetime import datetime

class RegulatoryUpdate(db.Model):
    __tablename__ = 'regulatory_updates'

    id = db.Column(db.Integer, primary_key=True)
    country = db.Column(db.String(100), nullable=True)
    regulator = db.Column(db.String(100), nullable=True)
    title = db.Column(db.String(500), nullable=False)
    summary = db.Column(db.Text, nullable=False)
    impact = db.Column(db.String(50), nullable=False) 
    url = db.Column(db.String(2048), unique=True, nullable=False) 
    
    generated_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    ai_one_liner = db.Column(db.String(500), nullable=True)
    obligations = db.Column(db.JSON, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'country': self.country,
            'regulator': self.regulator,
            'title': self.title,
            'summary': self.summary,
            'impact': self.impact,
            'url': self.url,
            'generated_at': self.generated_at.isoformat() if self.generated_at else None,
            'created_at': self.created_at.isoformat(),
            'ai_one_liner': self.ai_one_liner,
            'obligations': self.obligations
        }

class UpdateSubscription(db.Model):
    __tablename__ = 'update_subscriptions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    is_active = db.Column(db.Boolean, default=True)
    
    preferences = db.Column(db.JSON, nullable=True, default={}) 
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'email': self.email,
            'is_active': self.is_active,
            'preferences': self.preferences
        }

class UserUpdateReadStatus(db.Model):
    __tablename__ = 'user_update_read_status'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    update_id = db.Column(db.Integer, db.ForeignKey('regulatory_updates.id'), nullable=False)
    
    is_read = db.Column(db.Boolean, default=False)
    read_at = db.Column(db.DateTime, nullable=True)
    
    is_acknowledged = db.Column(db.Boolean, default=False)
    acknowledged_at = db.Column(db.DateTime, nullable=True)

    __table_args__ = (db.UniqueConstraint('user_id', 'update_id', name='uq_user_update_status'),)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'update_id': self.update_id,
            'is_read': self.is_read,
            'read_at': self.read_at.isoformat() if self.read_at else None,
            'is_acknowledged': self.is_acknowledged,
            'acknowledged_at': self.acknowledged_at.isoformat() if self.acknowledged_at else None
        }