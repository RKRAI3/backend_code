from flask import Blueprint, request, jsonify, g
from services.product_service import ProductService
from validators.schemas import ProductCreateSchema, ProductUpdateSchema
from utils.decorators import country_scope, validate_json
from models.user import SUPER_ADMIN, COUNTRY_ADMIN

ADMIN_ROLES = [SUPER_ADMIN, COUNTRY_ADMIN]

product_bp = Blueprint('products', __name__)

@product_bp.route('/all_product', methods=['GET'])
@country_scope()
def get_products(country_id):
    """Get all products of the user's country with pagination"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 10, type=int), 100)
        products_paginated = ProductService.get_all_products(page, per_page, country_id)
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
@country_scope(required=True, roles=ADMIN_ROLES)
@validate_json(ProductCreateSchema)
def create_product(validated_data, country_id):
    """Create a new product for the admin's country (super admin passes country_id)"""
    try:
        product, error = ProductService.create_product(validated_data, g.current_user.user_id, country_id)
        
        if error:
            return jsonify({'message': error}), 400
        
        return jsonify({
            'message': 'Product created successfully',
            'data': product.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({'message': f'Failed to create product: {str(e)}'}), 500

@product_bp.route('/<string:prod_id>', methods=['GET'])
@country_scope()
def get_product(prod_id, country_id):
    """Get product by ID"""
    try:
        product = ProductService.get_product_by_id(prod_id, country_id)
        if not product:
            return jsonify({'message': 'Product not found'}), 404
        
        return jsonify({
            'message': 'Product retrieved successfully',
            'data': product.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to retrieve product: {str(e)}'}), 500

@product_bp.route('/<string:prod_id>', methods=['PUT'])
@country_scope(roles=ADMIN_ROLES)
@validate_json(ProductUpdateSchema)
def update_product(validated_data, prod_id, country_id):
    """Update product information"""
    try:
        product, error = ProductService.update_product(prod_id, validated_data, country_id)
        if error:
            return jsonify({'message': error}), 400
        
        return jsonify({
            'message': 'Product updated successfully',
            'data': product.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to update product: {str(e)}'}), 500

@product_bp.route('/<string:prod_id>', methods=['DELETE'])
@country_scope(roles=ADMIN_ROLES)
def delete_product(prod_id, country_id):
    """Delete product"""
    try:
        success, error = ProductService.delete_product(prod_id, country_id)
        
        if error:
            return jsonify({'message': error}), 404 if 'not found' in error else 400
        
        return jsonify({
            'message': 'Product deleted successfully'
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to delete product: {str(e)}'}), 500
