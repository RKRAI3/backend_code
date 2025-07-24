from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.product_service import ProductService
from validators.schemas import ProductCreateSchema, ProductUpdateSchema
from utils.decorators import validate_json

product_bp = Blueprint('products', __name__)

@product_bp.route('/all_product', methods=['GET'])
@jwt_required()
def get_products():
    """Get all products with pagination"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 10, type=int), 100)
        products_paginated = ProductService.get_all_products(page, per_page)
        products = [product.to_dict() for product in products_paginated.items]
        fields_to_remove = ["updated_at", "created_at", "created_by"]
        # Process each item

        for item in products:
            # Remove unwanted fields
            for field in fields_to_remove:
                item.pop(field, None)
            # Rename prod_id to id
            item["id"] = item.pop("prod_id")
            item["price"] = item.pop("unit_price")
            
        # return jsonify(op_lst,200)
        return jsonify({
            'message': 'Products retrieved successfully',
            'data': products,
            "status":True
        }), 200
                # 'pagination': {
                #     'page': products_paginated.page,
                #     'per_page': products_paginated.per_page,
                #     'total': products_paginated.total,
                #     'pages': products_paginated.pages,
                #     'has_next': products_paginated.has_next,
                #     'has_prev': products_paginated.has_prev
                # }
            
        
        
    except Exception as e:
        return jsonify({'message': f'Failed to retrieve products: {str(e)}'}), 500

@product_bp.route('/', methods=['POST'])
@jwt_required()
@validate_json(ProductCreateSchema)
def create_product(validated_data):
    """Create a new product"""
    try:
        current_user_id = get_jwt_identity()
        product, error = ProductService.create_product(validated_data, current_user_id)
        
        if error:
            return jsonify({'message': error}), 400
        
        return jsonify({
            'message': 'Product created successfully',
            'data': product.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({'message': f'Failed to create product: {str(e)}'}), 500

@product_bp.route('/<int:prod_id>', methods=['GET'])
@jwt_required()
def get_product(prod_id):
    """Get product by ID"""
    try:
        product = ProductService.get_product_by_id(prod_id)
        if not product:
            return jsonify({'message': 'Product not found'}), 404
        
        return jsonify({
            'message': 'Product retrieved successfully',
            'data': product.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to retrieve product: {str(e)}'}), 500

@product_bp.route('/<int:prod_id>', methods=['PUT'])
@jwt_required()
@validate_json(ProductUpdateSchema)
def update_product(validated_data, prod_id):
    """Update product information"""
    try:
        product, error = ProductService.update_product(prod_id, validated_data)
        
        if error:
            return jsonify({'message': error}), 400
        
        return jsonify({
            'message': 'Product updated successfully',
            'data': product.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to update product: {str(e)}'}), 500

@product_bp.route('/<int:prod_id>', methods=['DELETE'])
@jwt_required()
def delete_product(prod_id):
    """Delete product"""
    try:
        success, error = ProductService.delete_product(prod_id)
        
        if error:
            return jsonify({'message': error}), 404 if 'not found' in error else 400
        
        return jsonify({
            'message': 'Product deleted successfully'
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to delete product: {str(e)}'}), 500
