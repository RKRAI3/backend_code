from models.product import Product
from app import db
from decimal import Decimal

class ProductService:
    @staticmethod
    def create_product(product_data, created_by_id):
        """Create a new product"""
        try:
            product = Product(
                name=product_data['name'],
                unit_price=product_data['unit_price'],
                created_by=created_by_id
            )
            db.session.add(product)
            db.session.commit()
            return product, None
        except Exception as e:
            db.session.rollback()
            return None, str(e)
    
    @staticmethod
    def get_all_products(page=1, per_page=10):
        """Get all active products with pagination"""
        products = Product.query.filter_by(deleted_at=None).paginate(
            page=page, per_page=per_page, error_out=False
        )
        return products
    
    @staticmethod
    def get_product_by_id(prod_id):
        """Get product by ID"""
        return Product.query.filter_by(prod_id=prod_id, deleted_at=None).first()
    
    @staticmethod
    def update_product(prod_id, update_data):
        """Update product information"""
        try:
            product = Product.query.filter_by(prod_id=prod_id, deleted_at=None).first()
            if not product:
                return None, "Product not found"
            
            for key, value in update_data.items():
                if value is not None and hasattr(product, key):
                    setattr(product, key, value)
            
            db.session.commit()
            return product, None
            
        except Exception as e:
            db.session.rollback()
            return None, str(e)
    
    @staticmethod
    def delete_product(prod_id):
        """Soft delete product"""
        try:
            product = Product.query.filter_by(prod_id=prod_id, deleted_at=None).first()
            if not product:
                return False, "Product not found"
            product.soft_delete()
            db.session.commit()
            return True, None
        except Exception as e:
            db.session.rollback()
            return False, str(e)