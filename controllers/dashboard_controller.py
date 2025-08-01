from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.dashboard_services import DashboardService
from utils.utility import transform_dashboard_data
from datetime import datetime, timedelta
# import logging

dashboard_bp = Blueprint('dashboard', __name__)

# Configure logging
# logger = logging.getLogger(__name__)

@dashboard_bp.route('/lastday_receipts', methods=['GET'])
@jwt_required()
def get_last_day_receipts_dashboard():
    """Get receipt dashboard with day-wise grouping and filtering"""
    try:
        yesterday = datetime.now() - timedelta(days=1)
        # Format as 'YYYY-MM-DD'
        formatted_yesterday = yesterday.strftime('%Y-%m-%d')
        start_date = formatted_yesterday
        end_date = start_date
        receipts_data, error = DashboardService.get_all_receipts_dashboard(
        start_date=start_date,
        end_date=end_date,
        )
        if error:
            return jsonify({
                'status': True,
                'message': "Failed to fetch the data of previous day"
            }), 400
        if not receipts_data:
            return jsonify({
                'status': True,
                'message': "There were no receipts created on the previous day."
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
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        # Validate pagination parameters
        if page < 1:
            return jsonify({
                'status': False,
                'message': 'Page number must be greater than 0'
            }), 400
        
        if per_page < 1 or per_page > 100:
            return jsonify({
                'status': False,
                'message': 'Per page must be between 1 and 100'
            }), 400
        
        # Call service
        result, error = DashboardService.get_receipts_dashboard(
            start_date=start_date,
            end_date=end_date,
            page=page,
            per_page=per_page
        )
        
        if error:
            return jsonify({
                'status': False,
                'message':"Failed to fetch the data for the given date period."
            }), 400
        if not result:
            return jsonify({
                'status': True,
                'message': "There were no receipts created for the selected time period"
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
