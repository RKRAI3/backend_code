from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from services.dashboard_services import DashboardService
from utils.utility import transform_dashboard_data
from datetime import datetime, timedelta
# import logging

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/today_receipts', methods=['GET'])
@jwt_required()
def get_today_receipts_dashboard():
    """Get receipt dashboard with day-wise grouping and filtering"""
    try:
        start_date = datetime.now().strftime('%Y-%m-%d')
        end_date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        # with app.app_context():
        receipts_data, error = DashboardService.get_all_receipts_dashboard(
        start_date=start_date,
        end_date=end_date,
        )
        if error:
            return jsonify({
                'status': False,
                'message': "Failed to fetch the data of current date"
            }), 400
        if not receipts_data:
            return jsonify({
                'status': True,
                'message': "No receipts have been issued for today yet."
            }), 400
        receipts_data=transform_dashboard_data(receipts_data)        
        return jsonify({
            "receipts_data": receipts_data,
            "status": True,
            "message": "Data Fetched successfully."
            }), 200
    except ValueError as e:
        return jsonify({
            'status': False,
            'message': f'Invalid parameter: {str(e)}'
        }), 400
    except Exception as e:
        return jsonify({
            'status': False,
            'message': 'Internal server error'
        }), 500

@dashboard_bp.route('/all_receipts', methods=['GET'])
@jwt_required()
def get_receipts_dashboard():
    """Get receipt dashboard with day-wise grouping and filtering"""
    try:
        # Get query parameters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        # page = int(request.args.get('page', 1))
        # per_page = int(request.args.get('per_page', 20))
        # Validate pagination parameters
        # if page < 1:
        #     return jsonify({
        #         'status': False,
        #         'message': 'Page number must be greater than 0'
        #     }), 400
        
        # if per_page < 1 or per_page > 100:
        #     return jsonify({
        #         'status': False,
        #         'message': 'Per page must be between 1 and 100'
        #     }), 400
        
        # Call service
        # with app.app_context():
        result, error = DashboardService.get_receipts_dashboard(
            start_date=start_date,
            end_date=end_date,
            # page=page,
            # per_page=per_page
        )
        
        if error:
            return jsonify({
                'status': False,
                'message':"Failed to fetch the data for the given date period."
            }), 400
        if not result['receipts_by_date']:
            return jsonify({
                'status': True,
                'message': "No receipts found for the selected time period"
            }), 400
        receipts_data=transform_dashboard_data(result["receipts_by_date"])  
        return jsonify({
            'status': True,
            'receipts_data': receipts_data
        }), 200
        
    except ValueError as e:
        return jsonify({
            'status': False,
            'message': f'Invalid parameter: {str(e)}'
        }), 400
    except Exception as e:
        return jsonify({
            'status': False,
            'message': f"Internal server error-{str(e)}"
        }), 500

@dashboard_bp.route('/dashboard-data', methods=['GET'])
def get_dashboard_data():
    print("Fetching dashboard data...")
    # Get the period parameter
    start_date = None
    end_date = None
    period = request.args.get('period', 'all')
    print(f"Received period: {period}")

    api_base_url = request.url_root.rstrip('/')
    currency = "₿"
    package = "Full Package"
    if "app1" in api_base_url:
        package = "Customer Convenience Package"
        currency = "₩"
    if period == 'today':
        # start_date = datetime.now().strftime('%Y-%m-%d')
        # end_date = start_date
        now = datetime.now()
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = now  # right now
    elif period == '7':
        # start_date = datetime.now().strftime('%Y-%m-%d')
        # end_date = datetime.now() - timedelta(days=7)
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    elif period == '30':
        # start_date = datetime.now().strftime('%Y-%m-%d')
        # end_date = datetime.now() - timedelta(days=30)
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    elif period == "custom":
        start_date = request.args.get("start_date")
        end_date = request.args.get("end_date")
        if start_date and end_date:
            start_date = datetime.strptime(start_date, "%Y-%m-%d").strftime('%Y-%m-%d')
            end_date = datetime.strptime(end_date, "%Y-%m-%d").strftime('%Y-%m-%d')

    # elif period == 'custom' and start_date and end_date:
    #     start_date = datetime.strptime(start_date, '%Y-%m-%d')
    #     end_date = datetime.strptime(end_date, '%Y-%m-%d')
    # elif period == 'all':
    #     start_date = datetime.strptime(start_date, '%Y-%m-%d')
    #     end_date = datetime.strptime(end_date, '%Y-%m-%d')
    print(f"Period: {period}, Start Date: {start_date}, End Date: {end_date}")
    response = DashboardService.get_dashboard_data(
        start_date=start_date,
        end_date=end_date,
        period=period,
        package = package,
        currency = currency
    )  
    # Convert back to the expected format for frontend
    print(f"Dashboard data response: {response}")
    return response
    