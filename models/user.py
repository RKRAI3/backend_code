from app import db, bcrypt
from datetime import datetime
from sqlalchemy import func
from sqlalchemy.orm import validates
import uuid

SUPER_ADMIN = 'super_admin'      # manages all countries; not tied to one
COUNTRY_ADMIN = 'country_admin'  # manages users/services of their own country
STAFF = 'staff'                  # generates receipts for their own country
ROLES = (SUPER_ADMIN, COUNTRY_ADMIN, STAFF)

class User(db.Model):
    __tablename__ = 'users'
    
    # user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()), unique=True, nullable=False)
    user_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)  # Increased length for MySQL
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    role = db.Column(db.String(20), default=STAFF, nullable=False)
    country_id = db.Column(db.String(36), db.ForeignKey('countries.country_id'), nullable=True, index=True)  # None only for super admin
    created_by = db.Column(db.String(36), db.ForeignKey('users.user_id'), nullable=True)
    created_at = db.Column(db.DateTime, default=func.now(), nullable=False)
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    created_users = db.relationship('User', backref=db.backref('creator', remote_side=[user_id]))
    created_products = db.relationship('Product', backref='creator', lazy=True)
    created_receipts = db.relationship('Receipt', backref='creator', lazy=True)
    
    def __init__(self, user_name, email, password, role=STAFF, country_id=None, created_by=None):
        self.user_name = user_name
        self.email = email
        self.password = password
        self.role = role
        self.country_id = country_id
        self.created_by = created_by

    @validates('role')
    def validate_role(self, key, value):
        if value not in ROLES:
            raise ValueError(f"Invalid role '{value}'")
        # Keep the legacy flag in sync for the existing admin_required checks
        self.is_admin = value in (SUPER_ADMIN, COUNTRY_ADMIN)
        return value

    @property
    def is_super_admin(self):
        return self.role == SUPER_ADMIN
    
    @property
    def password(self):
        raise AttributeError('Password is not readable')
    
    @password.setter
    def password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def verify_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)
    
    def soft_delete(self):
        self.deleted_at = func.now()
    
    def is_deleted(self):
        return self.deleted_at is not None
    
    def to_dict(self):
        return {
            'user_id': self.user_id,
            'user_name': self.user_name,
            'email': self.email,
            'is_admin': self.is_admin,
            'role': self.role,
            'country_id': self.country_id,
            'country': self.country.to_dict() if self.country else None,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }