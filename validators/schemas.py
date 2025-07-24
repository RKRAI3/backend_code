from pydantic import BaseModel, EmailStr, field_validator, Field
from typing import Optional, List
from decimal import Decimal

class UserCreateSchema(BaseModel):
    user_name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=50)
    is_admin: Optional[bool] = False
        
    @field_validator('user_name')
    @classmethod
    def validate_user_name(cls, v):
        if not v.replace(' ', '').replace('_', '').replace('-', '').isalnum():
            raise ValueError('Username can only contain letters, numbers, spaces, underscores, and hyphens')
        return v.strip()

class UserUpdateSchema(BaseModel):
    user_name: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[EmailStr] = None
    is_admin: Optional[bool] = None

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
        return round(v, 2)

class ProductUpdateSchema(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    unit_price: Optional[Decimal] = Field(None, gt=0)
    
    @field_validator('unit_price')
    @classmethod
    def validate_unit_price(cls, v):
        if v is not None:
            if v <= 0:
                raise ValueError('Unit price must be greater than 0')
            return round(v, 2)
        return v

class ReceiptItemSchema(BaseModel):
    prod_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0)

class ReceiptCreateSchema(BaseModel):
    items: List[ReceiptItemSchema] = Field(..., min_length=1)
    tax_rate: Optional[Decimal] = Field(default=Decimal('0'), ge=0, le=1)
    recipient_name: Optional[str] = Field(default=None, max_length=50)
    recipient_number: Optional[str] = Field(default=None, max_length=20)

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