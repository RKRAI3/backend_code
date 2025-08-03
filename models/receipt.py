from app import db
from datetime import datetime
from sqlalchemy import func
import uuid

class Receipt(db.Model):
    __tablename__ = 'receipts'
    receipt_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    receipt_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    recipient_name = db.Column(db.String(50), nullable=False)
    recipient_number = db.Column(db.String(20), nullable=True)
    total_amount = db.Column(db.Numeric(12, 2), nullable=False)
    tax_amount = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    gross_amount = db.Column(db.Numeric(12, 2), nullable=False)
    payment_mode = db.Column(db.String(20), nullable=False)
    transaction_number = db.Column(db.String(50), nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    created_at = db.Column(db.DateTime, default=func.now(), nullable=False)
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    receipt_items = db.relationship('ReceiptItem', backref='receipt', lazy=True, cascade='all, delete-orphan')
    
    def __init__(self, total_amount, tax_amount,gross_amount, created_by,recipient_number,recipient_name, payment_mode, transaction_number):
        self.receipt_number = self.generate_receipt_number()
        self.total_amount = total_amount
        self.tax_amount = tax_amount
        self.gross_amount = gross_amount
        self.created_by = created_by
        self.recipient_number = recipient_number
        self.recipient_name = recipient_name
        self.payment_mode = payment_mode
        self.transaction_number = transaction_number
    
    def generate_receipt_number(self):
        return f"REC-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
    
    def soft_delete(self):
        self.deleted_at = func.now()
    
    def is_deleted(self):
        return self.deleted_at is not None
    
    def to_dict(self):
        return {
            'receipt_id': self.receipt_id,
            'receipt_number': self.receipt_number,
            'recipient_name': self.recipient_name,
            'recipient_number': self.recipient_number,
            'total_amount': float(self.total_amount),
            'tax_amount': float(self.tax_amount),
            'gross_amount': float(self.gross_amount),
            'payment_mode': self.payment_mode,
            'transaction_number': self.transaction_number,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'items': [item.to_dict() for item in self.receipt_items if not item.is_deleted()]
        }