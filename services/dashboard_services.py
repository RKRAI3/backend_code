from models.receipt import Receipt
from models.receipt_item import ReceiptItem
from models.product import Product
from models.user import User
from app import db
from datetime import datetime, timedelta
from sqlalchemy import func, and_, or_, text
from decimal import Decimal
import pandas as pd
from flask import jsonify
from io import BytesIO
import base64
from services.sales_report_ver3 import generate_comprehensive_excel_report
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
                # date_key = receipt.created_at.strftime('%d-%m-%Y')
                date_key = receipt["created_at"]
                
                if date_key not in receipts_by_date:
                    receipts_by_date[date_key] = {
                        'date': date_key,
                        # 'day_name': receipt.created_at.strftime('%A'),
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


    # @staticmethod
    # def get_dashboard_data(start_date=None, end_date=None):
    #     """Get receipt dashboard with day-wise grouping and filtering"""
    #     response = {
    #         "status": False,
    #         "data": None,
    #         "message":"Something Went Worng."
    #         }
    #     try:
    #         # with app.app_context():
    #         # Build base query               
    #         query = Receipt.query.filter_by(deleted_at=None)
    #         # Apply date filters if provided
    #         if start_date:
    #             try:
    #                 # with app.app_context():
    #                 start_date = datetime.strptime(start_date, '%Y-%m-%d') + timedelta(days=1)
    #                 query = query.filter(Receipt.created_at <= start_date)
    #                 print("YAHA")
    #             except ValueError:
    #                 response["message"]= "Invalid start_date format. Use YYYY-MM-DD"
    #                 return response
    #                 # pass
    #         if end_date:
    #             try:
    #                 # with app.app_context():
    #                 # end_date = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
    #                 query = query.filter(Receipt.created_at > end_date)
    #                 print("waha")
    #             except ValueError:
    #                 response["message"]= "Invalid end_date format. Use YYYY-MM-DD"
    #                 return response
    #                 # pass
    #         # Order by latest first
    #         query = query.order_by(Receipt.created_at.desc())
    #         # receipts_items = query.receipt_items()
    #         receipts_paginated = query.all()  
    #         receipts_paginated = [rcpt.to_dict() for rcpt in receipts_paginated]
    #         if len(receipts_paginated)==0:
    #             response["message"]= "No Record available for the selected time period "
    #             return response
    #         print("AB")
    #         receipt_df = pd.DataFrame(receipts_paginated, columns=['receipt_id', 'receipt_number', 'recipient_name', 'package', 'package_amt', 'payment_mode', 'gross_amount', 'created_at'])
    #         itms_lst = []
    #         for rcpt in receipts_paginated:
    #             itms_lst.extend(rcpt["items"])
    #         items_df = pd.DataFrame(itms_lst, columns=['receipt_id','prod_id', 'quantity','std_price','vend_price','product_name','total_std_price','total_vend_price','created_at'])
    #         print("Merged DF after handling Full Package:\n", items_df.head())
    #         items_df['created_at'] = pd.to_datetime(items_df['created_at'], errors='coerce', dayfirst=True)
    #         items_df['created_at'] = items_df['created_at'].apply(
    #             lambda x: x.strftime("%d-%m-%YT%H:%M:%S") if pd.notnull(x) else None
    #         )

    #         # Get Full package Sevices from the receipt_df
    #         receipt_df1 = receipt_df[receipt_df['package']=='Full Package']
    #         receipt_df1 = receipt_df1.rename(columns={'package': 'product_name'})
    #         receipt_df1 = receipt_df1.rename(columns={'package_amt': 'std_price'})
    #         merged_df = pd.concat([items_df, receipt_df1], ignore_index=True, sort=False)
    #         merged_df["quantity"] = merged_df["quantity"].fillna(1)
    #         merged_df.drop(['prod_id','receipt_number', 'recipient_name', 'payment_mode', 'gross_amount'], axis=1, inplace=True)
    #         # Assuming your DataFrame is called df
    #         condition = (
    #             (merged_df['total_std_price'].isna()) & 
    #             (merged_df['product_name'] == 'Full Package')
    #         )

    #         merged_df.loc[condition, 'total_std_price'] = merged_df.loc[condition, 'std_price']
    #         merged_df.loc[condition, 'total_vend_price'] = merged_df.loc[condition, 'std_price']
    #         merged_df.loc[condition, 'vend_price'] = merged_df.loc[condition, 'std_price']
    #         response["status"] = True
    #         response["data"] = merged_df.to_dict('records')
            
    #         response['total_records'] = merged_df.shape[0]
    #         response['date_range'] = {
    #             'start': merged_df['created_at'].min() if not merged_df.empty else None,
    #             'end': merged_df['created_at'].max() if not merged_df.empty else None
    #         }
    #         response["message"] = "Dashboard data generated successfuly"
    #         return response
    #     except Exception as e:
    #         response["message"]= str(e)
    #         return response

    # ------------------ Helpers ------------------
    @staticmethod
    def group_revenue_over_time(df: pd.DataFrame, period: str):
        """Group revenue dynamically by period"""
        print(f"Grouping revenue for period: {period}")
        # if period == "today":
        #     df["period_group"] = df["created_at"].dt.strftime("%H:00")   # hourly
        if period == "today":
            print("Grouping by hour started",df['created_at'].head())
            df['created_at'] = pd.to_datetime(df['created_at'])
            df["period_group"] = df["created_at"].dt.strftime("%Y-%m-%d %H:%M")
        elif period == "7":
            df["period_group"] = df["created_at"].dt.strftime("%Y-%m-%d")  # daily
        elif period == "30":
            print("Grouping by week started")
            df["period_group"] = df["created_at"].dt.to_period("W").astype(str)  # weekly
            print("Grouping by week Finished")
        elif period in ["year", "all"]:
            df["period_group"] = df["created_at"].dt.strftime("%Y-%m")  # monthly
        else:
            df["period_group"] = df["created_at"].dt.strftime("%Y-%m-%d")
        print("Grouped DF:\n", df.head())
        df['total_std_price'] = df['total_std_price'].astype(int)
        return  (
            df.groupby("period_group")
            .agg(revenue=("total_vend_price", "sum"),
                receipts=("receipt_number", pd.Series.nunique))
            .reset_index()
            .rename(columns={"period_group": "date"})
            .to_dict("records")
        )

    @staticmethod
    def calc_trend(current, prev):
        """Calculate % change between current and previous values"""
        print(f"Calculating trend: current={current}, previous={prev}")
        if prev == 0:
            return "+0.0%"
        change = ((current - prev) / prev) * 100
        sign = "+" if change >= 0 else ""
        print(f"Calculated change: {sign}{change:.1f}%")
        return f"{sign}{change:.1f}%"


    def get_previous_period_data(start_date, end_date):
        """Fetch receipts for the previous period for trend comparison"""
        # Convert to datetime if needed
        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
        if isinstance(end_date, str):
            end_date = datetime.strptime(end_date, "%Y-%m-%d")

        print(f"Fetching previous period data for {start_date} to {end_date}")
        delta = end_date - start_date
        
        # Handle zero-length period (e.g., today)
        if delta.total_seconds() <= 0:
            delta = timedelta(days=1)
        
        prev_start = start_date - delta
        prev_end = start_date
        # with app.app_context():
        prev_query = Receipt.query.filter(
            Receipt.deleted_at.is_(None),
            Receipt.created_at >= prev_start,
            Receipt.created_at < prev_end
        ).all()
        # prev_query[0].to_dict()
            
        
        # print(f"Previous period receipts count: {len(prev_query)}")
        return [r.to_dict() for r in prev_query]
    
    
    # --- Growth Trend Calculation ---  
    def calc_growth_trend(*metrics_trends):
        """Calculate the average growth trend from individual metrics."""
        valid_trends = [trend for trend in metrics_trends if trend]  # Filter out None or invalid trends
        if not valid_trends:
            return "0.0%"  # No data to calculate the trend

        # Average the trends
        avg_trend = sum(float(trend.replace("%", "")) for trend in valid_trends) / len(valid_trends)
        return f"{avg_trend:.1f}%"
    
    @staticmethod
    def create_sales_report_data(df):
        print("create_sales_report_data function initialized")
        # Create the nested JSON report
        report = {}
        # Group by date and product name
        grouped = df.groupby([df['created_at'], 'product_name']).agg(
            total_quantity=('quantity', 'sum'),
            total_revenue=('total_vend_price', 'sum')
        ).reset_index()

        # Loop through grouped data and build the nested structure
        for _, row in grouped.iterrows():
            date = row['created_at'] # Format the date as 'date1', 'date2', etc.
            product = row['product_name']
            quantity = row['total_quantity']
            revenue = row['total_revenue']
            
            if date not in report:
                report[date] = {}
            
            report[date][product] = {'quantity': quantity, 'revenue': revenue}
            print("create_sales_report_data function finished")
        return report
    
    def periodic_product_revenue(currentproductRevenue, prev_productRevenue):
        # Combine both periods for comparison
        product_comparison = []
        current_products = {item['name']: item for item in currentproductRevenue}
        prev_products = {item['name']: item for item in prev_productRevenue}

        for product in currentproductRevenue:
            product_comparison.append({
                'name': product['name'],
                'current_revenue': product['revenue'],
                'prev_revenue': prev_products.get(product['name'], {}).get('revenue', 0),
                'current_quantity': product['quantity'],
                'prev_quantity': prev_products.get(product['name'], {}).get('quantity', 0),
            })
        # Add products that only existed in previous period
        for prev_product in prev_productRevenue:
            if prev_product['name'] not in current_products:
                product_comparison.append({
                    'name': prev_product['name'],
                    'current_revenue': 0,
                    'prev_revenue': prev_product['revenue'],
                    'current_quantity': 0,
                    'prev_quantity': prev_product['quantity']
                })
        return product_comparison

    # ------------------ Main Function ------------------
    @staticmethod
    def get_dashboard_data(start_date, end_date, package, currency,period="today"):
        """Get receipt dashboard with dynamic grouping and revenue trends"""
        response = {"status": False, "message": "Something went wrong", "data": None}
        try:
            # with app.app_context():
            query = Receipt.query.filter_by(deleted_at=None)
            # --- Apply date filters ---
            if start_date and not isinstance(start_date, datetime):
                try:
                    print("Parsing start_date:", start_date)
                    start_date = datetime.strptime(start_date, '%Y-%m-%d')
                except ValueError:
                    print("Invalid start_date format")
                    response["message"] = "Invalid start_date format. Use YYYY-MM-DD"
                    return jsonify(response, 400)
                    # return response
            if start_date and isinstance(start_date, datetime):
                query = query.filter(Receipt.created_at >= start_date)
                # receipts = query.order_by(Receipt.created_at.desc()).all()
                # receipts = [r.to_dict() for r in receipts]
                # print("result from start_date:", receipts)
            if end_date and not isinstance(end_date, datetime):
                try:
                    print("Parsing end_date:", end_date)
                    end_date = datetime.strptime(end_date, '%Y-%m-%d')
                    end_date = end_date + timedelta(days=1)
                    print("Filtering up to end_date (adjusted):", end_date)
                    query = query.filter(Receipt.created_at < end_date)
                except ValueError:
                    print("Invalid end_date format")
                    response["message"] = "Invalid end_date format. Use YYYY-MM-DD"
                    return jsonify(response, 400)
                    # return response
            print("End date before processing:", end_date)
            if end_date and isinstance(end_date, datetime):
                print("Filtering up to end_date:", start_date,end_date)
                end_date = end_date + timedelta(days=1)
                print("Filtering up to end_date (adjusted):", end_date)
                query = query.filter(Receipt.created_at < end_date)
            receipts = query.order_by(Receipt.created_at.desc()).all()
            receipts = [r.to_dict() for r in receipts]
            # print(f"Receipts are",receipts)
            if not receipts:
                response["message"] = "No records available for the selected time period"
                return jsonify(response, 204)
                # return response

            # --- Build DataFrames ---
            receipt_df = pd.DataFrame(receipts)
            print("Reeceipt DF", receipt_df)
            # receipt_df.to_csv(r"C:\Users\RAVI KANT\Documents\backend_code\ravi.csv")
            items = []
            for r in receipts:
                for itm in r['items']:
                    itm["receipt_number"] = r['receipt_number']
                #     itm["created_at"] = r['created_at']
                #     itm["package"] = r['package']
                items.extend(r["items"])
            items_df = pd.DataFrame(items)      
                 
            # Add Package as Services rows
            full_pkg = receipt_df[receipt_df["package"] == package].rename(
                columns={"package": "product_name", "gross_amount": "std_price"}
            )
            full_pkg = full_pkg.reset_index(drop=True)
                    
            tmp_df =items_df[items_df['receipt_id'].isin(full_pkg['receipt_id'])]
            tmp_df = tmp_df.drop_duplicates(subset=['receipt_id'], keep='first')
            tmp_df = tmp_df.reset_index(drop=True)
            
            full_pkg = full_pkg.merge(tmp_df[['receipt_id', 'created_at']], on='receipt_id', how='inner', suffixes=('', '_from_df1'))
            
            # Now, overwrite the 'created_at' column in df2 with the 'created_at_from_df1' from df1
            full_pkg['created_at'] = full_pkg['created_at_from_df1']
            # Drop the temporary column 'created_at_from_df1' if it's no longer needed
            full_pkg.drop(columns=['created_at_from_df1'], inplace=True)
            items_df = items_df[~items_df['receipt_number'].isin(full_pkg['receipt_number'])]
            merged_df = pd.concat([items_df, full_pkg], ignore_index=True, sort=False)
            merged_df["quantity"] = merged_df["quantity"].fillna(1)
            # merged_df["created_at"] = pd.to_datetime(merged_df["created_at"], errors="coerce")

            # Fix prices for Full Package
            cond = merged_df["product_name"] == package
            
            merged_df.loc[cond, "total_std_price"] = merged_df.loc[cond, "std_price"]
            merged_df.loc[cond, "total_vend_price"] = merged_df.loc[cond, "std_price"]
            merged_df.loc[cond, "vend_price"] = merged_df.loc[cond, "std_price"]
            merged_df.drop(['id', 'receipt_id', 'prod_id','free','recipient_name', 'recipient_number',
            'tot_vend_amt','tot_std_amt', 'tax_amount', 'payment_mode', 'transaction_number', 'created_by','updated_at','items'], axis =1, inplace=True)
            
            # --- Totals ---
            # merged_df.to_csv(r"C:\Users\RAVI KANT\Documents\backend_code\ravimerged.csv")
            totalReceipts = receipt_df.shape[0]
            totalRevenue = receipt_df['gross_amount'].sum()
            # totalRevenue = merged_df["total_vend_price"].sum()
            # total_vend_price is equalto gross_amount 
            totalStdRevenue = merged_df["total_std_price"].sum()
            totalProducts = merged_df["quantity"].sum()
            uniqueProducts = merged_df["product_name"].nunique()
            uniqueProductslist = merged_df["product_name"].unique().tolist()
            # --- Product Revenue breakdown ---
            productRevenue = (
                merged_df.groupby("product_name")
                .agg(revenue=("total_vend_price", "sum"),
                        quantity=("quantity", "sum"))
                .reset_index()
                .rename(columns={"product_name": "name"})
                .to_dict("records")
            )   
            # --- Price Comparison ---
            priceComparison = (
                merged_df.groupby("product_name")
                .agg(std_price=("std_price", "mean"),
                        vend_price=("vend_price", "mean"))
                .reset_index()
                .rename(columns={"product_name": "name"})
                .to_dict("records")
            )
            # priceComparison = (
            #     merged_df.groupby("product_name")
            #     .agg(std_price=("std_price", "sum"),
            #             vend_price=("vend_price", "sum"))
            #     .reset_index()
            #     .rename(columns={"product_name": "name"})
            #     .to_dict("records")
            # )
            revenueOverTime = DashboardService.group_revenue_over_time(merged_df, 'today')

            # with app.app_context():
            prev_receipts = DashboardService.get_previous_period_data(start_date, end_date) if (start_date and end_date) else []
            # print(f"Previous period receipts count: {len(prev_receipts)}")
            if prev_receipts:
                prev_items = []
                for r in prev_receipts:
                    prev_items.extend(r["items"])
                prev_df = pd.DataFrame(prev_items)
                prev_totalRevenue = prev_df["total_vend_price"].sum()
                prev_totalReceipts = len(prev_receipts)
                prev_totalProducts = prev_df["quantity"].sum()
                prev_uniqueProducts = prev_df["product_name"].nunique()
                # --- Product Revenue breakdown ---
                prev_productRevenue = (
                    prev_df.groupby("product_name")
                    .agg(revenue=("total_vend_price", "sum"),
                            quantity=("quantity", "sum"))
                    .reset_index()
                    .rename(columns={"product_name": "name"})
                    .to_dict("records")
                )   
            else:
                prev_totalRevenue = prev_totalReceipts = prev_totalProducts = prev_uniqueProducts = 0
                prev_productRevenue = []
            product_comparison = DashboardService.periodic_product_revenue(productRevenue, prev_productRevenue)
            revenueTrend = DashboardService.calc_trend(totalRevenue, prev_totalRevenue)
            receiptsTrend = DashboardService.calc_trend(totalReceipts, prev_totalReceipts)
            productTrend = DashboardService.calc_trend(totalProducts, prev_totalProducts)
            uniqueProductTrend = DashboardService.calc_trend(uniqueProducts, prev_uniqueProducts)

            # --- Calculate overall growth trend ---  
            growthTrend = DashboardService.calc_growth_trend(
                revenueTrend, receiptsTrend, productTrend, uniqueProductTrend
            )
            print(f"Calculated growth trend: {growthTrend}")
            if not receipts:
                response["message"] = "No records available for the selected time period 2ndTime"
                return jsonify(response, 204)
            receipt_df = pd.DataFrame(receipts)
            items = []
            for r in receipts:
                for itm in r['items']:
                    itm["receipt_number"] = r['receipt_number']
                    itm["created_at"] = r['created_at']
                    itm["package"] = r['package']
                items.extend(r["items"])
            items_df = pd.DataFrame(items)
            # print("Initial Items DF:\n", items_df.head())
            # Add Full Package rows
            full_pkg = receipt_df[receipt_df["package"] == package].rename(
                columns={"package": "product_name", "package_amt": "std_price"}
            )
            full_pkg['package'] = full_pkg['product_name']
            merged_df = pd.concat([items_df, full_pkg], ignore_index=True, sort=False)
            merged_df["quantity"] = merged_df["quantity"].fillna(1)
            # merged_df["created_at"] = pd.to_datetime(merged_df["created_at"], errors="coerce")

            # Fix prices for Full Package
            cond = merged_df["product_name"] == package
            merged_df.loc[cond, "total_std_price"] = merged_df.loc[cond, "std_price"]
            merged_df.loc[cond, "total_vend_price"] = merged_df.loc[cond, "std_price"]
            merged_df.loc[cond, "vend_price"] = merged_df.loc[cond, "std_price"]
            merged_df.drop(['id', 'receipt_id', 'prod_id','free','recipient_name', 'recipient_number',
            'tot_std_amt', 'tot_vend_amt', 'tax_amount', 'gross_amount',
            'payment_mode', 'transaction_number', 'created_by','updated_at','items','package'], axis =1, inplace=True)
            sales_report = DashboardService.create_sales_report_data(merged_df)
            df_qt = merged_df.pivot_table(index=["receipt_number","created_at"], columns="product_name", values="quantity", aggfunc="sum", fill_value=0)
            df_qt = df_qt.reset_index()
            
            df_prc = merged_df.pivot_table(index=["receipt_number", "created_at"], columns="product_name", values="total_vend_price", aggfunc="sum", fill_value=0)
            df_prc = df_prc.reset_index()
            if package in df_prc.columns:
                df_prc2 = df_prc[df_prc[package]!=0]
                df_prc1 = df_prc[df_prc[package]==0]
                df_prc1 = df_prc1[~df_prc1['receipt_number'].isin(df_prc2['receipt_number'])]
                df_prc = pd.concat([df_prc1, df_prc2], ignore_index=True, sort=False)
            df_prc = df_prc.sort_values(by='created_at', ascending=True)
            df_qt = df_qt.sort_values(by='created_at', ascending=True)
            # Generate Excel blob
            dashboard_data = {
                "period": period,
                "totalReceipts": totalReceipts,
                "totalRevenue": totalRevenue,
                "prev_totalRevenue": prev_totalRevenue,
                "totalStdRevenue": totalStdRevenue,
                "totalProducts": totalProducts,
                "uniqueProducts": uniqueProducts,
                "productRevenue": productRevenue,
                "product_comparison":product_comparison,
                "revenueOverTime": revenueOverTime,
                "priceComparison": priceComparison,
                "revenueTrend": revenueTrend,
                "receiptsTrend": receiptsTrend,
                "productTrend": productTrend,
                "uniqueProductTrend": uniqueProductTrend,
                "growthTrend": growthTrend,    # placeholder
                "quantity_report": df_qt.to_dict('records'),
                "revenue_report": df_prc.to_dict('records'),
                "sales_report": sales_report
            }
            excel_blob = generate_comprehensive_excel_report(dashboard_data, currency)
            # --- Final Response ---
            response["status"] = True
            response["message"] = "Dashboard data generated successfully"
            response["data"] = {
                "period": period,
                "totalReceipts": totalReceipts,
                "totalRevenue": totalRevenue,
                "prev_totalRevenue": prev_totalRevenue,
                "totalStdRevenue": totalStdRevenue,
                "totalProducts": totalProducts,
                "uniqueProducts": uniqueProducts,
                "productRevenue": productRevenue,
                "product_comparison":product_comparison,
                "revenueOverTime": revenueOverTime,
                "priceComparison": priceComparison,
                "revenueTrend": revenueTrend,
                "receiptsTrend": receiptsTrend,
                "productTrend": productTrend,
                "uniqueProductTrend": uniqueProductTrend,
                "growthTrend": growthTrend,    
                "quantity_report": df_qt.to_dict('records'),
                "revenue_report": df_prc.to_dict('records'),
                "uniqueProductslist": uniqueProductslist,
                "sales_report": excel_blob
            }
            response['period'] = period
            return jsonify(response, 200) 
        except Exception as e:
            response["message"] = str(e)
            return jsonify(response, 500)          