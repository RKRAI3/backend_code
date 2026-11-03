from models.product import Product
from models.country import Country
from app import db
from decimal import Decimal

class ProductService:
    @staticmethod
    def create_product(product_data, created_by_id, country_id):
        """Create a new product for a country"""
        try:
            country = Country.query.get(country_id)
            product = Product(
                name=product_data['name'],
                unit_price=country.quantize(product_data['unit_price']),
                created_by=created_by_id,
                country_id=country_id
            )
            db.session.add(product)
            db.session.commit()
            return product, None
        except Exception as e:
            db.session.rollback()
            return None, str(e)
    
    @staticmethod
    def _query(country_id=None):
        query = Product.query.filter_by(deleted_at=None)
        if country_id:
            query = query.filter_by(country_id=country_id)
        return query

    @staticmethod
    def get_all_products(page=1, per_page=10, country_id=None):
        """Get all active products with pagination, optionally limited to one country"""
        products = ProductService._query(country_id).paginate(
            page=page, per_page=per_page, error_out=False
        )
        return products
    
    @staticmethod
    def get_product_by_id(prod_id, country_id=None):
        """Get product by ID"""
        return ProductService._query(country_id).filter_by(prod_id=prod_id).first()
    
    @staticmethod
    def update_product(prod_id, update_data, country_id=None):
        """Update product information"""
        try:
            product = ProductService.get_product_by_id(prod_id, country_id)
            if not product:
                return None, "Product not found"
            
            for key, value in update_data.items():
                if value is not None and hasattr(product, key):
                    if key == 'unit_price':
                        value = product.country.quantize(value)
                    setattr(product, key, value)
            
            db.session.commit()
            return product, None
            
        except Exception as e:
            db.session.rollback()
            return None, str(e)
    
    @staticmethod
    def delete_product(prod_id, country_id=None):
        """Soft delete product"""
        try:
            product = ProductService.get_product_by_id(prod_id, country_id)
            if not product:
                return False, "Product not found"
            product.soft_delete()
            db.session.commit()
            return True, None
        except Exception as e:
            db.session.rollback()
            return False, str(e)