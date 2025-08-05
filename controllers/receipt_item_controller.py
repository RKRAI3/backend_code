from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from services.receipt_item_service import ReceiptItemService

receipt_item_bp = Blueprint('receipt_items', __name__)

@receipt_item_bp.route('/receipt/<string:receipt_id>/items', methods=['GET'])
@jwt_required()
def get_receipt_items_simple(receipt_id):
    """Get simple list of receipt items"""
    try:
        items, error = ReceiptItemService.get_items_by_receipt_id(receipt_id)
        
        if error:
            return jsonify({'message': error}), 404 if 'not found' in error else 400
        # with app.app_context():
        items_data = [item.to_dict() for item in items]
        
        return jsonify({
            'message': 'Receipt items retrieved successfully',
            'data': {
                'receipt_id': receipt_id,
                'items': items_data,
                'count': len(items_data)
            }
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to retrieve receipt items: {str(e)}'}), 500

@receipt_item_bp.route('/receipt/<string:receipt_id>/items/detailed', methods=['GET'])
@jwt_required()
def get_receipt_items_detailed(receipt_id):
    """Get receipt items with complete product information"""
    try:
        items, error = ReceiptItemService.get_items_with_product_details(receipt_id)
        
        if error:
            return jsonify({'message': error}), 404 if 'not found' in error else 400
        
        # Format items data
        items_data = []
        for item in items:
            items_data.append({
                'id': item.id,
                'receipt_id': item.receipt_id,
                'prod_id': item.prod_id,
                'product_name': item.product_name,
                'item_unit_price': float(item.item_unit_price),
                'current_unit_price': float(item.current_unit_price),
                'price_difference': float(item.current_unit_price - item.item_unit_price),
                'quantity': item.quantity,
                'total_amount': float(item.total_amount),
                'created_at': item.created_at.isoformat() if item.created_at else None,
                'updated_at': item.updated_at.isoformat() if item.updated_at else None
            })
        
        return jsonify({
            'message': 'Detailed receipt items retrieved successfully',
            'data': {
                'receipt_id': receipt_id,
                'items': items_data,
                'count': len(items_data)
            }
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to retrieve detailed receipt items: {str(e)}'}), 500

@receipt_item_bp.route('/receipt/<string:receipt_id>/items/statistics', methods=['GET'])
@jwt_required()
def get_receipt_items_statistics(receipt_id):
    """Get statistical information about receipt items"""
    try:
        statistics, error = ReceiptItemService.get_receipt_statistics(receipt_id)
        
        if error:
            return jsonify({'message': error}), 404 if 'not found' in error else 400
        
        return jsonify({
            'message': 'Receipt items statistics retrieved successfully',
            'data': {
                'receipt_id': receipt_id,
                'statistics': statistics
            }
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to retrieve receipt statistics: {str(e)}'}), 500

@receipt_item_bp.route('/receipt/<string:receipt_id>/items/breakdown', methods=['GET'])
@jwt_required()
def get_receipt_items_breakdown(receipt_id):
    """Get detailed product breakdown for receipt items"""
    try:
        breakdown, error = ReceiptItemService.get_product_breakdown(receipt_id)
        
        if error:
            return jsonify({'message': error}), 404 if 'not found' in error else 400
        
        # Calculate summary totals
        total_products = len(breakdown)
        grand_total_quantity = sum(product['total_quantity'] for product in breakdown)
        grand_total_amount = sum(product['total_amount'] for product in breakdown)
        
        return jsonify({
            'message': 'Receipt items breakdown retrieved successfully',
            'data': {
                'receipt_id': receipt_id,
                'summary': {
                    'total_products': total_products,
                    'grand_total_quantity': grand_total_quantity,
                    'grand_total_amount': round(grand_total_amount, 2)
                },
                'product_breakdown': breakdown
            }
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to retrieve receipt breakdown: {str(e)}'}), 500
