from app import db
from sqlalchemy import func
from decimal import Decimal
import uuid


class Country(db.Model):
    """Per-country configuration. Everything that used to live in .env / hardcoded
    strings (currency, tax, package name, business name) is stored here so a single
    deployment can serve every country."""
    __tablename__ = 'countries'

    country_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()), unique=True, nullable=False)
    code = db.Column(db.String(2), unique=True, nullable=False, index=True)  # ISO 3166-1 alpha-2, e.g. TH, KW
    name = db.Column(db.String(100), nullable=False)
    currency_code = db.Column(db.String(3), nullable=False)  # ISO 4217, e.g. THB, KWD
    currency_symbol = db.Column(db.String(10), nullable=False)
    currency_decimals = db.Column(db.Integer, nullable=False, default=2)  # KWD uses 3
    tax_rate = db.Column(db.Numeric(6, 4), nullable=False, default=0)  # 0.07 = 7%
    package_name = db.Column(db.String(36), nullable=True)  # e.g. "Full Package"; None = no package offered
    package_price = db.Column(db.Numeric(14, 3), nullable=True)  # fixed total charged for the package
    receipt_prefix = db.Column(db.String(10), nullable=False, default='IN')
    business_name = db.Column(db.String(100), nullable=True)
    alert_emails = db.Column(db.String(500), nullable=True)  # comma-separated
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, default=func.now(), nullable=False)
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    users = db.relationship('User', backref='country', lazy=True)
    products = db.relationship('Product', backref='country', lazy=True)
    receipts = db.relationship('Receipt', backref='country', lazy=True)

    def quantize(self, amount):
        """Round an amount to this country's currency precision"""
        return Decimal(str(amount)).quantize(Decimal(1).scaleb(-self.currency_decimals))

    def alert_email_list(self):
        return [e.strip() for e in (self.alert_emails or '').split(',') if e.strip()]

    def to_dict(self):
        return {
            'country_id': self.country_id,
            'code': self.code,
            'name': self.name,
            'currency_code': self.currency_code,
            'currency_symbol': self.currency_symbol,
            'currency_decimals': self.currency_decimals,
            'tax_rate': float(self.tax_rate),
            'package_name': self.package_name,
            'package_price': float(self.package_price) if self.package_price is not None else None,
            'receipt_prefix': self.receipt_prefix,
            'business_name': self.business_name,
            'alert_emails': self.alert_email_list(),
            'is_active': self.is_active,
        }
