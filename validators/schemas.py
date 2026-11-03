from pydantic import BaseModel, EmailStr, field_validator, Field
from typing import Optional, List, Literal
from decimal import Decimal
from uuid import UUID
from datetime import datetime

RoleType = Literal['super_admin', 'country_admin', 'staff']

class UserCreateSchema(BaseModel):
    user_name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=50)
    role: Optional[RoleType] = None
    is_admin: Optional[bool] = False  # legacy: used only when role is not given
    country_id: Optional[str] = Field(default=None, max_length=36)
        
    @field_validator('user_name')
    @classmethod
    def validate_user_name(cls, v):
        if not v.replace(' ', '').replace('_', '').replace('-', '').isalnum():
            raise ValueError('Username can only contain letters, numbers, spaces, underscores, and hyphens')
        return v.strip()

class UserUpdateSchema(BaseModel):
    user_name: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[EmailStr] = None
    role: Optional[RoleType] = None
    is_admin: Optional[bool] = None  # legacy: used only when role is not given
    country_id: Optional[str] = Field(default=None, max_length=36)

class CountryCreateSchema(BaseModel):
    code: str = Field(..., min_length=2, max_length=2)
    name: str = Field(..., min_length=2, max_length=100)
    currency_code: str = Field(..., min_length=3, max_length=3)
    currency_symbol: str = Field(..., min_length=1, max_length=10)
    currency_decimals: int = Field(default=2, ge=0, le=3)
    tax_rate: Decimal = Field(default=Decimal('0'), ge=0, le=1)
    package_name: Optional[str] = Field(default=None, max_length=36)
    package_price: Optional[Decimal] = Field(default=None, ge=0)
    receipt_prefix: str = Field(default='IN', min_length=1, max_length=10)
    business_name: Optional[str] = Field(default=None, max_length=100)
    alert_emails: Optional[List[EmailStr]] = None
    is_active: bool = True

    @field_validator('code', 'currency_code', 'receipt_prefix')
    @classmethod
    def upper(cls, v):
        return v.strip().upper()

class CountryUpdateSchema(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    currency_code: Optional[str] = Field(None, min_length=3, max_length=3)
    currency_symbol: Optional[str] = Field(None, min_length=1, max_length=10)
    currency_decimals: Optional[int] = Field(None, ge=0, le=3)
    tax_rate: Optional[Decimal] = Field(None, ge=0, le=1)
    package_name: Optional[str] = Field(None, max_length=36)
    package_price: Optional[Decimal] = Field(None, ge=0)
    receipt_prefix: Optional[str] = Field(None, min_length=1, max_length=10)
    business_name: Optional[str] = Field(None, max_length=100)
    alert_emails: Optional[List[EmailStr]] = None
    is_active: Optional[bool] = None

    @field_validator('currency_code', 'receipt_prefix')
    @classmethod
    def upper(cls, v):
        return v.strip().upper() if v else v

class LoginSchema(BaseModel):
    email: EmailStr
    password: str

class ProductCreateSchema(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    unit_price: Decimal = Field(..., gt=0)
        
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        return v.strip()
        
    @field_validator('unit_price')
    @classmethod
    def validate_unit_price(cls, v):
        if v <= 0:
            raise ValueError('Unit price must be greater than 0')
        return round(v, 3)

class ProductUpdateSchema(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    unit_price: Optional[Decimal] = Field(None, gt=0)
    
    @field_validator('unit_price')
    @classmethod
    def validate_unit_price(cls, v):
        if v is not None:
            if v <= 0:
                raise ValueError('Unit price must be greater than 0')
            return round(v, 3)
        return v

# class ReceiptItemSchema(BaseModel):
#     prod_id: UUID = Field(..., description="Product UUID")
#     quantity: int = Field(..., gt=0)
#     is_free: Optional[bool] = False
class ReceiptItemBase(BaseModel):
    prod_id: str = Field(..., min_length=36, max_length=40, description="Product UUID")
    is_free: Optional[bool] = Field(default=False)
    quantity: Decimal = Field(..., gt=0)
    vendor_price: Decimal = Field(..., ge=0)

class ReceiptItemCreate(ReceiptItemBase):
    pass

class ReceiptItemResponse(ReceiptItemBase):
    id: str
    total_std_price: Decimal
    total_vend_price: Decimal
    created_at: datetime


class ReceiptCreateSchema(BaseModel):
    items: List[ReceiptItemBase] = Field(..., min_length=1)
    package: Optional[str] = Field(default='Standard', max_length=36)
    package_amt: Optional[Decimal] = Field(default=Decimal('0'), ge=0)
    tax_rate: Optional[Decimal] = Field(default=Decimal('0'), ge=0, le=1)
    recipient_name: Optional[str] = Field(default=None, max_length=50)
    recipient_number: Optional[str] = Field(default=None, max_length=20)
    payment_mode: str = Field(default='CASH', max_length=20)
    transaction_number: Optional[str] = Field(default=None, max_length=50)
    @field_validator('tax_rate')
    @classmethod
    def validate_tax_rate(cls, v):
        if v is not None:
            return round(v, 4)
        return v
        
    @field_validator('items')
    @classmethod
    def validate_items(cls, v):
        if not v:
            raise ValueError('At least one item is required')
                
        # Check for duplicate products
        prod_ids = [item.prod_id for item in v]
        if len(prod_ids) != len(set(prod_ids)):
            raise ValueError('Duplicate products are not allowed')
        return v