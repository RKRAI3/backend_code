from models.receipt import Receipt
from models.receipt_item import ReceiptItem
from models.product import Product
from models.user import User
from app import db
from datetime import datetime, timedelta
from sqlalchemy import func, and_, or_, text
from decimal import Decimal

class DashboardService:

    @staticmethod
    def get_all_receipts_dashboard(start_date=None, end_date=None):
        """Get all receipt dashboard with day-wise between the """
        try:
            # Build base query
            # with app.app_context():
            query = Receipt.query.filter_by(deleted_at=None)
            # Apply date filters if provided
            if start_date:
                try:
                    start_dt = datetime.strptime(start_date, '%Y-%m-%d')
                    query = query.filter(Receipt.created_at >= start_dt)
                except ValueError:
                    return None, "Invalid start_date format. Use YYYY-MM-DD"
                    # pass
            if end_date:
                try:
                    end_dt = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
                    query = query.filter(Receipt.created_at < end_dt)
                except ValueError:
                    return None, "Invalid end_date format. Use YYYY-MM-DD"
                    # pass
            query = query.order_by(Receipt.created_at.desc())
            receipts = query.all()
            # Group receipts by date
            receipts_by_date = {}
            for receipt in receipts:
                date_key = receipt.created_at.strftime('%d-%m-%Y')
                # Initialize date entry if not exists
                if date_key not in receipts_by_date:
                    receipts_by_date[date_key] = {
                        'date': date_key,
                        'day_name': receipt.created_at.strftime('%A'),
                        'receipts': [],
                        'day_summary': {
                            'total_receipts': 0,
                            'total_amount': 0.00,
                            'total_tax': 0.00,
                            'total_items': 0
                        }
                    }
                # Add receipt details
                receipt_data = receipt.to_dict()
                receipt_data['items_count'] = len(receipt.receipt_items)
                receipts_by_date[date_key]['receipts'].append(receipt_data)
                # Update day summary
                receipts_by_date[date_key]['day_summary']['total_receipts'] += 1
                receipts_by_date[date_key]['day_summary']['total_amount'] += float(receipt.gross_amount)
                # receipts_by_date[date_key]['day_summary']['total_tax'] += float(receipt.tax_amount)
                receipts_by_date[date_key]['day_summary']['total_items'] += len(receipt.receipt_items)
            # Round amounts
            for date_data in receipts_by_date.values():
                date_data['day_summary']['total_amount'] = round(date_data['day_summary']['total_amount'], 2)
                date_data['day_summary']['total_tax'] = round(date_data['day_summary']['total_tax'], 2)
            # Convert to sorted list (latest first)
            receipts_list = list(receipts_by_date.values())
            return receipts_list, None
        except Exception as e:
            return None, str(e)


    @staticmethod
    def get_receipts_dashboard(start_date=None, end_date=None):
        """Get receipt dashboard with day-wise grouping and filtering"""
        try:
            # Build base query               
            query = Receipt.query.filter_by(deleted_at=None)
            # Apply date filters if provided
            if start_date:
                try:
                    # with app.app_context():
                    start_dt = datetime.strptime(start_date, '%Y-%m-%d')
                    query = query.filter(Receipt.created_at >= start_dt)
                except ValueError:
                    return None, "Invalid start_date format. Use YYYY-MM-DD"
                    # pass
            if end_date:
                try:
                    # with app.app_context():
                    end_dt = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
                    query = query.filter(Receipt.created_at < end_dt)
                except ValueError:
                    return None, "Invalid end_date format. Use YYYY-MM-DD"
                    # pass
            # Order by latest first
            query = query.order_by(Receipt.created_at.desc())
                    
            # Paginate results
            # receipts_paginated = query.paginate(
            #     page=page, per_page=per_page, error_out=False
            # )
            receipts_paginated = query.all()
            # Group receipts by date
            receipts_by_date = {}
            for receipt in receipts_paginated.items:                
                date_key = receipt.created_at.strftime('%d-%m-%Y')
                if date_key not in receipts_by_date:
                    receipts_by_date[date_key] = {
                        'date': date_key,
                        'day_name': receipt.created_at.strftime('%A'),
                        'receipts': [],
                        'day_summary': {
                            'total_receipts': 0,
                            'total_amount': 0.00,
                            'total_tax': 0.00,
                            'total_items': 0
                        }
                    }
                # Add receipt details
                receipt_data = receipt.to_dict()
                receipt_data['items_count'] = len(receipt.receipt_items)
                receipts_by_date[date_key]['receipts'].append(receipt_data)
                # Update day summary
                receipts_by_date[date_key]['day_summary']['total_receipts'] += 1
                receipts_by_date[date_key]['day_summary']['total_amount'] += float(receipt.gross_amount)
                receipts_by_date[date_key]['day_summary']['total_tax'] += float(receipt.tax_amount)
                receipts_by_date[date_key]['day_summary']['total_items'] += len(receipt.receipt_items)
                
            # Round amounts
            for date_data in receipts_by_date.values():
                date_data['day_summary']['total_amount'] = round(date_data['day_summary']['total_amount'], 2)
                date_data['day_summary']['total_tax'] = round(date_data['day_summary']['total_tax'], 2)
            # Convert to sorted list (latest first)
            receipts_list = list(receipts_by_date.values())
            return {
                'receipts_by_date': receipts_list,
                # 'pagination': {
                #     'page': receipts_paginated.page,
                #     'per_page': receipts_paginated.per_page,
                #     'total': receipts_paginated.total,
                #     'pages': receipts_paginated.pages,
                #     'has_next': receipts_paginated.has_next,
                #     'has_prev': receipts_paginated.has_prev
                # }
            }, None
            
        except Exception as e:
            return None, str(e)