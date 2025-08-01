from models.receipt import Receipt
from models.receipt_item import ReceiptItem
from models.product import Product
from app import db
from decimal import Decimal
from environment import TAX_RATE



class ReceiptService:
    TAX_RATE = Decimal(TAX_RATE)
    @staticmethod
    def create_receipt(receipt_data, created_by_id,):
        """Create a new receipt with items"""
        try:
            items_data = receipt_data['items']
            # tax_rate = receipt_data.get('tax_rate', 0)
            tax_rate = ReceiptService.TAX_RATE
            recipient_name = receipt_data['recipient_name']
            recipient_number = receipt_data['recipient_number']
            # Validate products exist and calculate amounts
            subtotal = Decimal('0.00')
            receipt_items = []
            
            for item_data in items_data:
                product = Product.query.filter_by(
                    prod_id=item_data['prod_id'], 
                    deleted_at=None
                ).first()
                
                if not product:
                    return None, f"Product with ID {item_data['prod_id']} not found"
                
                item_total = product.unit_price * item_data['quantity']
                subtotal += item_total
                
                receipt_items.append({
                    'prod_id': product.prod_id,
                    'unit_price': product.unit_price,
                    'quantity': item_data['quantity'],
                    'total_amount': item_total
                })
            
            # Calculate tax and total
            tax_amount = subtotal * Decimal(str(tax_rate))
            total_amount = subtotal + tax_amount
            
            # Create receipt
            receipt = Receipt(
                recipient_name=recipient_name,
                recipient_number=recipient_number,
                total_amount=subtotal,
                tax_amount=tax_amount,
                gross_amount=total_amount,
                created_by=created_by_id
            )
            
            db.session.add(receipt)
            db.session.flush()  # Get receipt ID
            
            # Create receipt items
            for item_data in receipt_items:
                receipt_item = ReceiptItem(
                    receipt_id=receipt.receipt_id,
                    prod_id=item_data['prod_id'],
                    unit_price=item_data['unit_price'],
                    quantity=item_data['quantity']
                )
                db.session.add(receipt_item)
            
            db.session.commit()
            return receipt, None
            
        except Exception as e:
            db.session.rollback()
            return None, str(e)
    
    @staticmethod
    def get_all_receipts(current_user_id, page=1, per_page=10):
        """Get all active receipts with pagination"""
        qry = Receipt.query.filter_by(deleted_at=None, created_by=current_user_id)
        receipts = qry.order_by(Receipt.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
        return receipts
    
    @staticmethod
    def get_receipt_by_id(receipt_id):
        """Get receipt by ID with items"""
        return Receipt.query.filter_by(receipt_id=receipt_id, deleted_at=None).first()
    
    @staticmethod
    def get_receipt_by_number(receipt_number):
        """Get receipt by receipt number"""
        return Receipt.query.filter_by(receipt_number=receipt_number, deleted_at=None).first()


    @staticmethod
    def get_receipt_items_by_receipt_id(receipt_id):
        """Get all items for a specific receipt"""
        try:
            # First check if receipt exists
            receipt = Receipt.query.filter_by(receipt_id=receipt_id, deleted_at=None).first()
            if not receipt:
                return None, "Receipt not found"
            
            # Get all active receipt items for this receipt
            receipt_items = ReceiptItem.query.filter_by(
                receipt_id=receipt_id, 
                deleted_at=None
            ).join(Product).filter(Product.deleted_at == None).all()
            
            return receipt_items, None
            
        except Exception as e:
            return None, str(e)
    
    @staticmethod
    def get_receipt_items_with_details(receipt_id):
        """Get receipt items with detailed product information"""
        try:
            # Check if receipt exists
            receipt = Receipt.query.filter_by(receipt_id=receipt_id, deleted_at=None).first()
            if not receipt:
                return None, "Receipt not found"
            
            # Query receipt items with product details
            items_query = db.session.query(
                ReceiptItem.id,
                ReceiptItem.receipt_id,
                ReceiptItem.prod_id,
                ReceiptItem.unit_price,
                ReceiptItem.quantity,
                ReceiptItem.total_amount,
                ReceiptItem.created_at,
                Product.name.label('product_name'),
                Product.unit_price.label('current_product_price')
            ).join(
                Product, ReceiptItem.prod_id == Product.prod_id
            ).filter(
                ReceiptItem.receipt_id == receipt_id,
                ReceiptItem.deleted_at == None,
                Product.deleted_at == None
            ).all()
            
            # Convert to dictionary format
            items_list = []
            for item in items_query:
                items_list.append({
                    'id': item.id,
                    'receipt_id': item.receipt_id,
                    'prod_id': item.prod_id,
                    'product_name': item.product_name,
                    'unit_price': float(item.unit_price),
                    'current_product_price': float(item.current_product_price),
                    'quantity': item.quantity,
                    'total_amount': float(item.total_amount),
                    'created_at': item.created_at.isoformat() if item.created_at else None
                })
            
            return items_list, None
            
        except Exception as e:
            return None, str(e)
    
   
    @staticmethod
    def delete_receipt(receipt_id):
        """Soft delete receipt"""
        try:
            receipt = Receipt.query.filter_by(receipt_id=receipt_id, deleted_at=None).first()
            if not receipt:
                return False, "Receipt not found"
            
            receipt.soft_delete()
            # Also soft delete receipt items
            for item in receipt.receipt_items:
                item.soft_delete()
            
            db.session.commit()
            return True, None
            
        except Exception as e:
            db.session.rollback()
            return False, str(e)
    
