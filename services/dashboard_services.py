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
                    # return None, "Invalid start_date format. Use YYYY-MM-DD"
                    pass
            if end_date:
                try:
                    end_dt = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
                    query = query.filter(Receipt.created_at < end_dt)
                except ValueError:
                    # return None, "Invalid end_date format. Use YYYY-MM-DD"
                    pass
            query = query.order_by(Receipt.created_at.desc())
            receipts = query.all()
            
        # Group receipts by date
            receipts_by_date = {}
            for receipt in receipts:
                date_key = receipt.created_at.strftime('%Y-%m-%d')
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
                receipts_by_date[date_key]['day_summary']['total_amount'] += float(receipt.total_amount)
                receipts_by_date[date_key]['day_summary']['total_tax'] += float(receipt.tax_amount)
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
    def get_receipts_dashboard(start_date=None, end_date=None, page=1, per_page=20):
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
            
            if end_date:
                try:
                    # with app.app_context():
                    end_dt = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
                    query = query.filter(Receipt.created_at < end_dt)
                except ValueError:
                    return None, "Invalid end_date format. Use YYYY-MM-DD"
            # Order by latest first
            query = query.order_by(Receipt.created_at.desc())
                
            # Paginate results
            receipts_paginated = query.paginate(
                page=page, per_page=per_page, error_out=False
            )
        
            # Group receipts by date
            receipts_by_date = {}
            for receipt in receipts_paginated.items:
                date_key = receipt.created_at.strftime('%Y-%m-%d')
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
                receipts_by_date[date_key]['day_summary']['total_amount'] += float(receipt.total_amount)
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
                'pagination': {
                    'page': receipts_paginated.page,
                    'per_page': receipts_paginated.per_page,
                    'total': receipts_paginated.total,
                    'pages': receipts_paginated.pages,
                    'has_next': receipts_paginated.has_next,
                    'has_prev': receipts_paginated.has_prev
                }
            }, None
            
        except Exception as e:
            return None, str(e)
    
    @staticmethod
    def get_dashboard_summary(start_date=None, end_date=None):
        """Get overall dashboard summary statistics"""
        try:
            # Build base query
            query = Receipt.query.filter_by(deleted_at=None)
            
            # Apply date filters
            if start_date:
                start_dt = datetime.strptime(start_date, '%Y-%m-%d')
                query = query.filter(Receipt.created_at >= start_dt)
            
            if end_date:
                end_dt = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
                query = query.filter(Receipt.created_at < end_dt)
            
            # Get summary statistics
            summary_stats = query.with_entities(
                func.count(Receipt.receipt_id).label('total_receipts'),
                func.sum(Receipt.total_amount).label('total_revenue'),
                func.sum(Receipt.tax_amount).label('total_tax'),
                func.avg(Receipt.total_amount).label('average_receipt_value'),
                func.min(Receipt.created_at).label('oldest_receipt'),
                func.max(Receipt.created_at).label('latest_receipt')
            ).first()
            
            # Get total items count
            items_query = db.session.query(
                func.count(ReceiptItem.id).label('total_items'),
                func.sum(ReceiptItem.quantity).label('total_quantity')
            ).join(Receipt).filter(
                Receipt.deleted_at == None,
                ReceiptItem.deleted_at == None
            )
            
            if start_date:
                start_dt = datetime.strptime(start_date, '%Y-%m-%d')
                items_query = items_query.filter(Receipt.created_at >= start_dt)
            
            if end_date:
                end_dt = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
                items_query = items_query.filter(Receipt.created_at < end_dt)
            
            items_stats = items_query.first()
            
            # Get top products
            top_products = db.session.query(
                Product.name,
                func.sum(ReceiptItem.quantity).label('total_sold'),
                func.sum(ReceiptItem.total_amount).label('total_revenue')
            ).join(ReceiptItem).join(Receipt).filter(
                Receipt.deleted_at == None,
                ReceiptItem.deleted_at == None,
                Product.deleted_at == None
            )
            
            if start_date:
                start_dt = datetime.strptime(start_date, '%Y-%m-%d')
                top_products = top_products.filter(Receipt.created_at >= start_dt)
            
            if end_date:
                end_dt = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
                top_products = top_products.filter(Receipt.created_at < end_dt)
            
            top_products = top_products.group_by(Product.prod_id, Product.name)\
                                     .order_by(func.sum(ReceiptItem.total_amount).desc())\
                                     .limit(5).all()
            
            # Format response
            summary = {
                'period': {
                    'start_date': start_date,
                    'end_date': end_date,
                    'oldest_receipt': summary_stats.oldest_receipt.isoformat() if summary_stats.oldest_receipt else None,
                    'latest_receipt': summary_stats.latest_receipt.isoformat() if summary_stats.latest_receipt else None
                },
                'totals': {
                    'total_receipts': summary_stats.total_receipts or 0,
                    'total_revenue': float(summary_stats.total_revenue or 0),
                    'total_tax': float(summary_stats.total_tax or 0),
                    'total_items': items_stats.total_items or 0,
                    'total_quantity': items_stats.total_quantity or 0
                },
                'averages': {
                    'average_receipt_value': float(summary_stats.average_receipt_value or 0),
                    'average_items_per_receipt': round((items_stats.total_items or 0) / max(summary_stats.total_receipts or 1, 1), 2)
                },
                'top_products': [
                    {
                        'name': product.name,
                        'total_sold': product.total_sold,
                        'total_revenue': float(product.total_revenue)
                    }
                    for product in top_products
                ]
            }
            
            return summary, None
            
        except Exception as e:
            return None, str(e)
    
    @staticmethod
    def get_daily_analytics(start_date=None, end_date=None):
        """Get day-wise analytics for charts and graphs"""
        try:
            # Set default date range if not provided (last 30 days)
            if not end_date:
                end_date = datetime.now().strftime('%Y-%m-%d')
            if not start_date:
                start_dt = datetime.now() - timedelta(days=30)
                start_date = start_dt.strftime('%Y-%m-%d')
            
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            end_dt = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
            
            # Get daily statistics
            daily_stats = db.session.query(
                func.date(Receipt.created_at).label('date'),
                func.count(Receipt.receipt_id).label('receipt_count'),
                func.sum(Receipt.total_amount).label('daily_revenue'),
                func.sum(Receipt.tax_amount).label('daily_tax'),
                func.avg(Receipt.total_amount).label('avg_receipt_value')
            ).filter(
                Receipt.deleted_at == None,
                Receipt.created_at >= start_dt,
                Receipt.created_at < end_dt
            ).group_by(func.date(Receipt.created_at))\
             .order_by(func.date(Receipt.created_at).desc()).all()
            
            # Format daily analytics
            analytics = []
            for stat in daily_stats:
                analytics.append({
                    'date': stat.date.strftime('%Y-%m-%d'),
                    'day_name': stat.date.strftime('%A'),
                    'receipt_count': stat.receipt_count,
                    'daily_revenue': float(stat.daily_revenue),
                    'daily_tax': float(stat.daily_tax),
                    'avg_receipt_value': float(stat.avg_receipt_value)
                })
            
            return analytics, None
            
        except Exception as e:
            return None, str(e)
    
    @staticmethod
    def get_hourly_analytics(date=None):
        """Get hourly breakdown for a specific date"""
        try:
            if not date:
                date = datetime.now().strftime('%Y-%m-%d')
            
            target_date = datetime.strptime(date, '%Y-%m-%d')
            next_date = target_date + timedelta(days=1)
            
            # Get hourly statistics
            hourly_stats = db.session.query(
                func.extract('hour', Receipt.created_at).label('hour'),
                func.count(Receipt.receipt_id).label('receipt_count'),
                func.sum(Receipt.total_amount).label('hourly_revenue')
            ).filter(
                Receipt.deleted_at == None,
                Receipt.created_at >= target_date,
                Receipt.created_at < next_date
            ).group_by(func.extract('hour', Receipt.created_at))\
             .order_by(func.extract('hour', Receipt.created_at)).all()
            
            # Format hourly analytics
            analytics = []
            for stat in hourly_stats:
                hour = int(stat.hour)
                time_label = f"{hour:02d}:00-{(hour+1):02d}:00"
                analytics.append({
                    'hour': hour,
                    'time_range': time_label,
                    'receipt_count': stat.receipt_count,
                    'hourly_revenue': float(stat.hourly_revenue)
                })
            
            return {
                'date': date,
                'hourly_breakdown': analytics
            }, None
            
        except Exception as e:
            return None, str(e)
    
    @staticmethod
    def search_receipts(search_term, start_date=None, end_date=None, page=1, per_page=20):
        """Search receipts by receipt number, user email, or product name"""
        try:
            # Build base query with joins
            query = db.session.query(Receipt).join(User, Receipt.created_by == User.user_id)\
                             .outerjoin(ReceiptItem, Receipt.receipt_id == ReceiptItem.receipt_id)\
                             .outerjoin(Product, ReceiptItem.prod_id == Product.prod_id)\
                             .filter(Receipt.deleted_at == None)
            
            # Apply search filters
            if search_term:
                search_filter = or_(
                    Receipt.receipt_number.ilike(f'%{search_term}%'),
                    User.email.ilike(f'%{search_term}%'),
                    User.user_name.ilike(f'%{search_term}%'),
                    Product.name.ilike(f'%{search_term}%')
                )
                query = query.filter(search_filter)
            
            # Apply date filters
            if start_date:
                start_dt = datetime.strptime(start_date, '%Y-%m-%d')
                query = query.filter(Receipt.created_at >= start_dt)
            
            if end_date:
                end_dt = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
                query = query.filter(Receipt.created_at < end_dt)
            
            # Remove duplicates and order
            query = query.distinct().order_by(Receipt.created_at.desc())
            
            # Paginate
            receipts_paginated = query.paginate(
                page=page, per_page=per_page, error_out=False
            )
            
            # Format results
            results = []
            for receipt in receipts_paginated.items:
                receipt_data = receipt.to_dict()
                receipt_data['creator_name'] = receipt.creator.user_name if receipt.creator else 'Unknown'
                receipt_data['creator_email'] = receipt.creator.email if receipt.creator else 'Unknown'
                receipt_data['items_count'] = len(receipt.receipt_items)
                results.append(receipt_data)
            
            return {
                'search_results': results,
                'search_term': search_term,
                'pagination': {
                    'page': receipts_paginated.page,
                    'per_page': receipts_paginated.per_page,
                    'total': receipts_paginated.total,
                    'pages': receipts_paginated.pages,
                    'has_next': receipts_paginated.has_next,
                    'has_prev': receipts_paginated.has_prev
                }
            }, None
            
        except Exception as e:
            return None, str(e)
