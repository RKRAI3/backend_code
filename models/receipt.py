from app import db
from datetime import datetime
from sqlalchemy import func
import uuid
from sqlalchemy.orm import validates

class Receipt(db.Model):
    __tablename__ = 'receipts'
    # receipt_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    receipt_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()), unique=True, nullable=False)
    receipt_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    recipient_name = db.Column(db.String(50), nullable=False)
    recipient_number = db.Column(db.String(20), nullable=True)
    package = db.Column(db.String(36), nullable=False, default='Standard')
    package_amt = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    total_std_amount = db.Column(db.Numeric(12, 2), nullable=False)
    total_vend_amount = db.Column(db.Numeric(12, 2), nullable=False)
    tax_amount = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    gross_amount = db.Column(db.Numeric(12, 2), nullable=False)
    payment_mode = db.Column(db.String(20), nullable=False)
    transaction_number = db.Column(db.String(50), nullable=True)
    created_by = db.Column(db.String(36),db.ForeignKey('users.user_id'), nullable=False)
    created_at = db.Column(db.DateTime, default=func.now(), nullable=False)
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = db.Column(db.DateTime, nullable=True)

    # Relationships
    receipt_items = db.relationship('ReceiptItem', backref='receipt', lazy=True, cascade='all, delete-orphan')
    
    def __init__(self,package, package_amt, total_std_amount, total_vend_amount, tax_amount,gross_amount, created_by,recipient_number,recipient_name, payment_mode, transaction_number,):
        self.receipt_number = self.generate_receipt_number()
        self.package = package
        self.package_amt = package_amt
        self.total_std_amount = total_std_amount
        self.total_vend_amount = total_vend_amount
        self.tax_amount = tax_amount
        self.gross_amount = gross_amount
        self.created_by = created_by
        self.recipient_number = recipient_number
        self.recipient_name = recipient_name
        self.payment_mode = payment_mode
        self.transaction_number = transaction_number
    
    @validates('package')
    def on_active_change(self, key, value):
        if value and value.lower is "Full Package":
            self.total_std_amount = 0
            self.total_vend_amount = 0
        return value
        
    
    def generate_receipt_number(self):
        return f"IN-{datetime.now().strftime('%d%m%Y')}-{str(uuid.uuid4())[:8].upper()}"
    # def generate_receipt_number(self):
    #     return f"REC-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"

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
            "package": self.package,
            'package_amt': float(self.package_amt),
            'tot_std_amt': float(self.total_std_amount),
            'tot_vend_amt': float(self.total_vend_amount),
            'tax_amount': float(self.tax_amount),
            'gross_amount': float(self.gross_amount),
            'payment_mode': self.payment_mode,
            'transaction_number': self.transaction_number,
            'created_by': self.created_by,
            'created_at': self.created_at.strftime('%d-%m-%Y') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%d-%m-%Y') if self.updated_at else None,
            'items': [item.to_dict() for item in self.receipt_items if not item.is_deleted()]
        }