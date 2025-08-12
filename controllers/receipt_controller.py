from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.receipt_service import ReceiptService
from validators.schemas import ReceiptCreateSchema
from utils.decorators import validate_json
from utils.utility import transform_receipt_data, transform_pre_generated_receipts_list

receipt_bp = Blueprint('receipts', __name__)

@receipt_bp.route('/all_receipts', methods=['GET'])
@jwt_required()
def get_receipts():
    """Get all receipts with pagination"""
    try:
        current_user_id = get_jwt_identity()
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 10, type=int), 100)
        receipts = ReceiptService.get_all_receipts(current_user_id, page, per_page)

        if not receipts:
            return jsonify({'message': 'Receipt not found'}), 404
        data = transform_pre_generated_receipts_list(receipts)
        response = {"receipt_list": data}
        response["message"] = 'Receipts retrieved successfully'
        response["status"] = True
        return jsonify(response),200
        
    except Exception as e:
        return jsonify({'message': f'Failed to retrieve receipts: {str(e)}'}), 500

@receipt_bp.route('/create-receipt', methods=['POST'])
@jwt_required()
@validate_json(ReceiptCreateSchema)
def create_receipt(validated_data):
    """Create a new receipt"""
    try:
        current_user_id = get_jwt_identity()
        print("Payload", validated_data)
        receipt, error = ReceiptService.create_receipt(validated_data, current_user_id)
        if error:
            return jsonify({'message inner': error}), 400
        return jsonify({
            'message': 'Receipt created successfully',
            'data': receipt.to_dict()
        }), 201
    except Exception as e:
        return jsonify({'message': f'Failed to create receipt: {str(e)}'}), 500

@receipt_bp.route('get-receipt/<string:receipt_id>', methods=['GET'])
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


@receipt_bp.route('/<string:receipt_id>/items', methods=['GET'])
@jwt_required()
def get_receipt_items(receipt_id):
    """Get all items for a specific receipt"""
    try:
        items, error = ReceiptService.get_receipt_items_with_details(receipt_id)
        
        if error:
            return jsonify({'message': error}), 404 if 'not found' in error else 400
        
        return jsonify({
            'message': 'Receipt items retrieved successfully',
            'data': {
                'receipt_id': receipt_id,
                'items': items,
                'total_items': len(items),
                'total_quantity': sum(item['quantity'] for item in items),
                'subtotal': sum(item['total_amount'] for item in items)
            }
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to retrieve receipt items: {str(e)}'}), 500

@receipt_bp.route('/<string:receipt_id>/items/summary', methods=['GET'])
@jwt_required()
def get_receipt_items_summary(receipt_id):
    """Get receipt items summary with aggregated information"""
    try:
        items, error = ReceiptService.get_receipt_items_with_details(receipt_id)
        
        if error:
            return jsonify({'message': error}), 404 if 'not found' in error else 400
        
        # Calculate summary statistics
        total_items = len(items)
        total_quantity = sum(item['quantity'] for item in items)
        subtotal = sum(item['total_amount'] for item in items)
        
        # Group items by product for analysis
        product_summary = {}
        for item in items:
            prod_id = item['prod_id']
            if prod_id not in product_summary:
                product_summary[prod_id] = {
                    'product_name': item['product_name'],
                    'quantity': 0,
                    'total_amount': 0,
                    'unit_price': item['unit_price']
                }
            product_summary[prod_id]['quantity'] += item['quantity']
            product_summary[prod_id]['total_amount'] += item['total_amount']
        
        return jsonify({
            'message': 'Receipt items summary retrieved successfully',
            'data': {
                'receipt_id': receipt_id,
                'summary': {
                    'total_items': total_items,
                    'total_quantity': total_quantity,
                    'subtotal': subtotal
                },
                'product_breakdown': list(product_summary.values()),
                'items': items
            }
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to retrieve receipt items summary: {str(e)}'}), 500


@receipt_bp.route('/<string:receipt_id>', methods=['DELETE'])
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
