from app import db
from datetime import datetime
from sqlalchemy import func
from sqlalchemy.orm import validates
import uuid

class ReceiptItem(db.Model):
    __tablename__ = 'receipt_items'
    # id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()), unique=True, nullable=False)
    receipt_id = db.Column(db.String(36), db.ForeignKey('receipts.receipt_id'), nullable=False)
    prod_id = db.Column(db.String(36), db.ForeignKey('products.prod_id'), nullable=False)
    is_free = db.Column(db.Boolean, default=False, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    std_price = db.Column(db.Numeric(10, 2), nullable=False)
    vendor_price = db.Column(db.Numeric(10, 2), nullable=False)
    total_std_price = db.Column(db.Numeric(12, 2), nullable=False)
    total_vend_price = db.Column(db.Numeric(12, 2), nullable=False)
    created_at = db.Column(db.DateTime, default=func.now(), nullable=False)
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = db.Column(db.DateTime, nullable=True)
    
    def __init__(self, receipt_id, prod_id, is_free, quantity, std_price, vendor_price):
        self.receipt_id = receipt_id
        self.prod_id = prod_id
        self.is_free= is_free
        self.quantity = quantity
        if is_free:
            self.std_price = 0
            self.vendor_price = 0
            self.total_std_price = 0
            self.total_vend_price = 0
        else:
            self.std_price = std_price
            self.vendor_price = vendor_price
            self.total_std_price = std_price * quantity
            self.total_vend_price = vendor_price * quantity
        # self.std_price = std_price
        # self.vendor_price = vendor_price
        # self.quantity = quantity
        # self.total_std_price = std_price * quantity
        # self.total_vend_price = vendor_price * quantity
    

    # @validates('is_free')
    # def on_is_free_change(self, key, value):
    #     if value:
    #         self.std_price = 0
    #         self.vendor_price = 0
    #         self.total_std_price = 0
    #         self.total_vend_price = 0
    #     return value
    
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
            'std_price': float(self.std_price),
            'vend_price': float(self.vendor_price),
            'quantity': self.quantity,
            'total_std_price': float(self.total_std_price),
            'total_vend_price': float(self.total_vend_price),
            'free': self.is_free,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }