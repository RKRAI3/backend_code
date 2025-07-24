from app import db
from datetime import datetime
from sqlalchemy import func

class Product(db.Model):
    __tablename__ = 'products'
    
    prod_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(200), nullable=False)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    created_at = db.Column(db.DateTime, default=func.now(), nullable=False)
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    receipt_items = db.relationship('ReceiptItem', backref='product', lazy=True)
    
    def soft_delete(self):
        self.deleted_at = func.now()
    
    def is_deleted(self):
        return self.deleted_at is not None
    
    def to_dict(self):
        return {
            'prod_id': self.prod_id,
            'service': self.name,
            'unit_price': float(self.unit_price),
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
