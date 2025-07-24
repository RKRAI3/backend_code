from models.receipt_item import ReceiptItem
from models.receipt import Receipt
from models.product import Product
from app import db
from decimal import Decimal

class ReceiptItemService:
    @staticmethod
    def get_items_by_receipt_id(receipt_id, include_deleted=False):
        """Get all receipt items for a specific receipt"""
        try:
            # Verify receipt exists
            receipt = Receipt.query.filter_by(receipt_id=receipt_id).first()
            if not receipt:
                return None, "Receipt not found"
            
            if not include_deleted and receipt.is_deleted():
                return None, "Receipt not found"
            
            # Build query
            # with app.app_context():
            query = ReceiptItem.query.filter_by(receipt_id=receipt_id)
            items = query.all()
            if not include_deleted:
                query = query.filter_by(deleted_at=None)
            # with app.app_context():
            items = query.all()
            return items, None
            
        except Exception as e:
            return None, str(e)
    
    @staticmethod
    def get_items_with_product_details(receipt_id):
        """Get receipt items with complete product information"""
        try:
            # Verify receipt exists and is not deleted
            receipt = Receipt.query.filter_by(receipt_id=receipt_id, deleted_at=None).first()
            if not receipt:
                return None, "Receipt not found"
            
            # Query with JOIN to get product details
            items_with_products = db.session.query(
                ReceiptItem.id,
                ReceiptItem.receipt_id,
                ReceiptItem.prod_id,
                ReceiptItem.unit_price.label('item_unit_price'),
                ReceiptItem.quantity,
                ReceiptItem.total_amount,
                ReceiptItem.created_at,
                ReceiptItem.updated_at,
                Product.name.label('product_name'),
                Product.unit_price.label('current_unit_price'),
                Product.created_by.label('product_created_by')
            ).join(
                Product, ReceiptItem.prod_id == Product.prod_id
            ).filter(
                ReceiptItem.receipt_id == receipt_id,
                ReceiptItem.deleted_at == None,
                Product.deleted_at == None
            ).order_by(ReceiptItem.created_at).all()
            
            return items_with_products, None
            
        except Exception as e:
            return None, str(e)
    
    @staticmethod
    def get_receipt_statistics(receipt_id):
        """Get statistical information about receipt items"""
        try:
            items, error = ReceiptItemService.get_items_with_product_details(receipt_id)
            if error:
                return None, error
            
            if not items:
                return {
                    'total_items': 0,
                    'total_quantity': 0,
                    'subtotal': 0.00,
                    'average_item_price': 0.00,
                    'most_expensive_item': None,
                    'most_quantity_item': None
                }, None
            
            # Calculate statistics
            total_items = len(items)
            total_quantity = sum(item.quantity for item in items)
            subtotal = sum(float(item.total_amount) for item in items)
            average_item_price = subtotal / total_items if total_items > 0 else 0
            
            # Find most expensive and highest quantity items
            most_expensive = max(items, key=lambda x: float(x.total_amount))
            most_quantity = max(items, key=lambda x: x.quantity)
            
            statistics = {
                'total_items': total_items,
                'total_quantity': total_quantity,
                'subtotal': round(subtotal, 2),
                'average_item_price': round(average_item_price, 2),
                'most_expensive_item': {
                    'product_name': most_expensive.product_name,
                    'quantity': most_expensive.quantity,
                    'total_amount': float(most_expensive.total_amount)
                },
                'most_quantity_item': {
                    'product_name': most_quantity.product_name,
                    'quantity': most_quantity.quantity,
                    'total_amount': float(most_quantity.total_amount)
                }
            }
            
            return statistics, None
            
        except Exception as e:
            return None, str(e)
    
    @staticmethod
    def get_product_breakdown(receipt_id):
        """Get detailed breakdown by product"""
        try:
            items, error = ReceiptItemService.get_items_with_product_details(receipt_id)
            if error:
                return None, error
            
            # Group by product
            product_breakdown = {}
            
            for item in items:
                prod_id = item.prod_id
                if prod_id not in product_breakdown:
                    product_breakdown[prod_id] = {
                        'prod_id': prod_id,
                        'product_name': item.product_name,
                        'item_unit_price': float(item.item_unit_price),
                        'current_unit_price': float(item.current_unit_price),
                        'price_difference': float(item.current_unit_price - item.item_unit_price),
                        'total_quantity': 0,
                        'total_amount': 0.00,
                        'line_items': []
                    }
                
                # Add to totals
                product_breakdown[prod_id]['total_quantity'] += item.quantity
                product_breakdown[prod_id]['total_amount'] += float(item.total_amount)
                
                # Add line item details
                product_breakdown[prod_id]['line_items'].append({
                    'id': item.id,
                    'quantity': item.quantity,
                    'unit_price': float(item.item_unit_price),
                    'total_amount': float(item.total_amount),
                    'created_at': item.created_at.isoformat() if item.created_at else None
                })
            
            # Round totals
            for product in product_breakdown.values():
                product['total_amount'] = round(product['total_amount'], 2)
                product['price_difference'] = round(product['price_difference'], 2)
            
            return list(product_breakdown.values()), None
            
        except Exception as e:
            return None, str(e)
