from app import db
from datetime import datetime
from sqlalchemy import func
import uuid

class ReceiptItem(db.Model):
    __tablename__ = 'receipt_items'
    
    # id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()), unique=True, nullable=False)
    receipt_id = db.Column(db.String(36), db.ForeignKey('receipts.receipt_id'), nullable=False)
    prod_id = db.Column(db.String(36), db.ForeignKey('products.prod_id'), nullable=False)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    total_amount = db.Column(db.Numeric(12, 2), nullable=False)
    created_at = db.Column(db.DateTime, default=func.now(), nullable=False)
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = db.Column(db.DateTime, nullable=True)
    
    def __init__(self, receipt_id, prod_id, unit_price, quantity):
        self.receipt_id = receipt_id
        self.prod_id = prod_id
        self.unit_price = unit_price
        self.quantity = quantity
        self.total_amount = unit_price * quantity
    
    def soft_delete(self):
        self.deleted_at = func.now()
    
    def is_deleted(self):
        return self.deleted_at is not None
    
    def to_dict(self):
        return {
            'id': self.id,
            'receipt_id': self.receipt_id,
            'prod_id': self.prod_id,
            'product_name': self.product.name if self.product else None,
            'unit_price': float(self.unit_price),
            'quantity': self.quantity,
            'total_amount': float(self.total_amount),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }