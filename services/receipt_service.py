from models.receipt import Receipt
from models.receipt_item import ReceiptItem
from models.product import Product
from app import db
from decimal import Decimal



class ReceiptService:
    TAX_RATE = Decimal('0.10')  # Default tax rate of 15%
    @staticmethod
    def create_receipt(receipt_data, created_by_id):
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
    def get_all_receipts(page=1, per_page=10):
        """Get all active receipts with pagination"""
        receipts = Receipt.query.filter_by(deleted_at=None).paginate(
            page=page, per_page=per_page, error_out=False
        )
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
    
