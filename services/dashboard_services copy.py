from models.receipt import Receipt
from models.receipt_item import ReceiptItem
from models.product import Product
from models.user import User
from app import db
from datetime import datetime, timedelta
from sqlalchemy import func, and_, or_, text
from decimal import Decimal
import pandas as pd

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
                    # start_date = datetime.strptime(start_date, '%Y-%m-%d')
                    query = query.filter(Receipt.created_at >= start_date)
                except ValueError:
                    return None, "Invalid start_date format. Use YYYY-MM-DD"
                    # pass
            if end_date:
                try:
                    end_date = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
                    end_date = end_date + timedelta(days=1)
                    query = query.filter(Receipt.created_at < end_date)
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
            # with app.app_context():
            # Build base query               
            query = Receipt.query.filter_by(deleted_at=None)
            # Apply date filters if provided
            if start_date:
                try:
                    # with app.app_context():
                    start_dt = datetime.strptime(start_date, '%Y-%m-%d')
                    query = query.filter(Receipt.created_at >= start_dt)
                except ValueError:
                    # return None, "Invalid start_date format. Use YYYY-MM-DD"
                    pass
            if end_date:
                try:
                    # with app.app_context():
                    end_dt = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
                    query = query.filter(Receipt.created_at < end_dt)
                except ValueError:
                    # return None, "Invalid end_date format. Use YYYY-MM-DD"
                    pass
            # Order by latest first
            query = query.order_by(Receipt.created_at.desc())
            # receipts_items = query.receipt_items()
            receipts_paginated = query.all()  
            receipts_paginated = [rcpt.to_dict() for rcpt in receipts_paginated]
            # Paginate results
            # receipts_paginated = query.paginate(
            #     page=page, per_page=per_page, error_out=False
            # )
            receipts_paginated = query.all()
            # Group receipts by date
            receipts_by_date = {}
            for receipt in receipts_paginated:                
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
        def get_receipts_dashboard(start_date=None, end_date=None):
            """Get receipt dashboard with day-wise grouping and filtering"""
            try:
                with app.app_context():
                    # Build base query               
                    query = Receipt.query.filter_by(deleted_at=None)
                    # Apply date filters if provided
                    if start_date:
                        try:
                            # with app.app_context():
                            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
                            query = query.filter(Receipt.created_at >= start_dt)
                        except ValueError:
                            # return None, "Invalid start_date format. Use YYYY-MM-DD"
                            pass
                    if end_date:
                        try:
                            # with app.app_context():
                            end_dt = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
                            query = query.filter(Receipt.created_at < end_dt)
                        except ValueError:
                            # return None, "Invalid end_date format. Use YYYY-MM-DD"
                            pass
                    # Order by latest first
                    query = query.order_by(Receipt.created_at.desc())
                    # receipts_items = query.receipt_items()
                    receipts_paginated = query.all()  
                    receipts_paginated = [rcpt.to_dict() for rcpt in receipts_paginated]
                # Paginate results
                # receipts_paginated = query.paginate(
                #     page=page, per_page=per_page, error_out=False
                # )
                receipts_paginated = query.all()
                # Group receipts by date
                receipts_by_date = {}
                for receipt in receipts_paginated:                
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


    @staticmethod
    def get_dashboard_data(start_date=None, end_date=None):
        """Get receipt dashboard with day-wise grouping and filtering"""
        response = {
            "status": False,
            "data": None,
            "message":"Something Went Worng."
            }
        try:
            # with app.app_context():
            # Build base query               
            query = Receipt.query.filter_by(deleted_at=None)
            # Apply date filters if provided
            if start_date:
                try:
                    # with app.app_context():
                    start_date = datetime.strptime(start_date, '%Y-%m-%d') + timedelta(days=1)
                    query = query.filter(Receipt.created_at <= start_date)
                    print("YAHA")
                except ValueError:
                    response["message"]= "Invalid start_date format. Use YYYY-MM-DD"
                    return response
                    # pass
            if end_date:
                try:
                    # with app.app_context():
                    # end_date = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
                    query = query.filter(Receipt.created_at > end_date)
                    print("waha")
                except ValueError:
                    response["message"]= "Invalid end_date format. Use YYYY-MM-DD"
                    return response
                    # pass
            # Order by latest first
            query = query.order_by(Receipt.created_at.desc())
            # receipts_items = query.receipt_items()
            receipts_paginated = query.all()  
            receipts_paginated = [rcpt.to_dict() for rcpt in receipts_paginated]
            if len(receipts_paginated)==0:
                response["message"]= "No Record available for the selected time period "
                return response
            print("AB")
            receipt_df = pd.DataFrame(receipts_paginated, columns=['receipt_id', 'receipt_number', 'recipient_name', 'package', 'package_amt', 'payment_mode', 'gross_amount', 'created_at'])
            itms_lst = []
            for rcpt in receipts_paginated:
                itms_lst.extend(rcpt["items"])
            items_df = pd.DataFrame(itms_lst, columns=['receipt_id','prod_id', 'quantity','std_price','vend_price','product_name','total_std_price','total_vend_price','created_at'])
            print("Merged DF after handling Full Package:\n", items_df.head())
            items_df['created_at'] = pd.to_datetime(items_df['created_at'], errors='coerce', dayfirst=True)
            items_df['created_at'] = items_df['created_at'].apply(
                lambda x: x.strftime("%d-%m-%YT%H:%M:%S") if pd.notnull(x) else None
            )

            # Get Full package Sevices from the receipt_df
            receipt_df1 = receipt_df[receipt_df['package']=='Full Package']
            receipt_df1 = receipt_df1.rename(columns={'package': 'product_name'})
            receipt_df1 = receipt_df1.rename(columns={'package_amt': 'std_price'})
            merged_df = pd.concat([items_df, receipt_df1], ignore_index=True, sort=False)
            merged_df["quantity"] = merged_df["quantity"].fillna(1)
            merged_df.drop(['prod_id','receipt_number', 'recipient_name', 'payment_mode', 'gross_amount'], axis=1, inplace=True)
            # Assuming your DataFrame is called df
            condition = (
                (merged_df['total_std_price'].isna()) & 
                (merged_df['product_name'] == 'Full Package')
            )

            merged_df.loc[condition, 'total_std_price'] = merged_df.loc[condition, 'std_price']
            merged_df.loc[condition, 'total_vend_price'] = merged_df.loc[condition, 'std_price']
            merged_df.loc[condition, 'vend_price'] = merged_df.loc[condition, 'std_price']
            response["status"] = True
            response["data"] = merged_df.to_dict('records')
            
            response['total_records'] = merged_df.shape[0]
            response['date_range'] = {
                'start': merged_df['created_at'].min() if not merged_df.empty else None,
                'end': merged_df['created_at'].max() if not merged_df.empty else None
            }
            response["message"] = "Dashboard data generated successfuly"
            return response
        except Exception as e:
            response["message"]= str(e)
            return response