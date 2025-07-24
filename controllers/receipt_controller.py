from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.receipt_service import ReceiptService
from validators.schemas import ReceiptCreateSchema
from utils.decorators import validate_json
from utils.utility import transform_receipt_data

receipt_bp = Blueprint('receipts', __name__)

@receipt_bp.route('/', methods=['GET'])
@jwt_required()
def get_receipts():
    """Get all receipts with pagination"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 10, type=int), 100)
        receipts_paginated = ReceiptService.get_all_receipts(page, per_page)
        return jsonify({
            'message': 'Receipts retrieved successfully',
            'data': {
                'receipts': [receipt.to_dict() for receipt in receipts_paginated.items],
                'pagination': {
                    'page': receipts_paginated.page,
                    'per_page': receipts_paginated.per_page,
                    'total': receipts_paginated.total,
                    'pages': receipts_paginated.pages,
                    'has_next': receipts_paginated.has_next,
                    'has_prev': receipts_paginated.has_prev
                }
            }
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to retrieve receipts: {str(e)}'}), 500

@receipt_bp.route('/', methods=['POST'])
@jwt_required()
@validate_json(ReceiptCreateSchema)
def create_receipt(validated_data):
    """Create a new receipt"""
    try:
        current_user_id = get_jwt_identity()
        print(f"Validated Data is: {validated_data}")
        receipt, error = ReceiptService.create_receipt(validated_data, current_user_id)
        
        if error:
            return jsonify({'message': error}), 400
        
        return jsonify({
            'message': 'Receipt created successfully',
            'data': receipt.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({'message': f'Failed to create receipt: {str(e)}'}), 500

@receipt_bp.route('/<int:receipt_id>', methods=['GET'])
@jwt_required()
def get_receipt(receipt_id):
    """Get receipt by ID"""
    try:
        receipt = ReceiptService.get_receipt_by_id(receipt_id)
        if not receipt:
            return jsonify({'message': 'Receipt not found'}), 404
        
        # return jsonify({
        #     'message': 'Receipt retrieved successfully',
        #     'data': receipt.to_dict()
        # }), 200
        response = transform_receipt_data(receipt.to_dict())
        response["message"] = 'Receipts retrieved successfully'
        response["status"] = True
        return jsonify(response),200
        
    except Exception as e:
        return jsonify({'message': f'Failed to retrieve receipt: {str(e)}'}), 500

@receipt_bp.route('/number/<receipt_number>', methods=['GET'])
@jwt_required()
def get_receipt_by_number(receipt_number):
    """Get receipt by receipt number"""
    try:
        receipt = ReceiptService.get_receipt_by_number(receipt_number)
        if not receipt:
            return jsonify({'message': 'Receipt not found'}), 404
        
        return jsonify({
            'message': 'Receipt retrieved successfully',
            'data': receipt.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to retrieve receipt: {str(e)}'}), 500

@receipt_bp.route('/<int:receipt_id>', methods=['DELETE'])
@jwt_required()
def delete_receipt(receipt_id):
    """Delete receipt"""
    try:
        success, error = ReceiptService.delete_receipt(receipt_id)
        
        if error:
            return jsonify({'message': error}), 404 if 'not found' in error else 400
        
        return jsonify({
            'message': 'Receipt deleted successfully'
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to delete receipt: {str(e)}'}), 500
