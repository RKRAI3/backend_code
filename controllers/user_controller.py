from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.user_service import UserService
from validators.schemas import UserCreateSchema, UserUpdateSchema
from utils.decorators import admin_required, validate_json

user_bp = Blueprint('users', __name__)

@user_bp.route('/', methods=['GET'])
@jwt_required()
def get_users():
    """Get all users with pagination"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 10, type=int), 100)
        
        users_paginated = UserService.get_all_users(page, per_page)
        
        return jsonify({
            'message': 'Users retrieved successfully',
            'data': {
                'users': [user.to_dict() for user in users_paginated.items],
                'pagination': {
                    'page': users_paginated.page,
                    'per_page': users_paginated.per_page,
                    'total': users_paginated.total,
                    'pages': users_paginated.pages,
                    'has_next': users_paginated.has_next,
                    'has_prev': users_paginated.has_prev
                }
            }
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to retrieve users: {str(e)}'}), 500

@user_bp.route('/', methods=['POST'])
@admin_required
@validate_json(UserCreateSchema)
def create_user(validated_data):
    """Create a new user (Admin only)"""
    try:
        current_user_id = get_jwt_identity()
        user, error = UserService.create_user(validated_data, current_user_id)
        
        if error:
            return jsonify({'message': error}), 400
        
        return jsonify({
            'message': 'User created successfully',
            'data': user.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({'message': f'Failed to create user: {str(e)}'}), 500

@user_bp.route('/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    """Get user by ID"""
    try:
        user = UserService.get_user_by_id(user_id)
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        return jsonify({
            'message': 'User retrieved successfully',
            'data': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to retrieve user: {str(e)}'}), 500

@user_bp.route('/<int:user_id>', methods=['PUT'])
@admin_required
@validate_json(UserUpdateSchema)
def update_user(validated_data, user_id):
    """Update user information (Admin only)"""
    try:
        user, error = UserService.update_user(user_id, validated_data)
        
        if error:
            return jsonify({'message': error}), 400
        
        return jsonify({
            'message': 'User updated successfully',
            'data': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to update user: {str(e)}'}), 500

@user_bp.route('/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    """Delete user (Admin only)"""
    try:
        success, error = UserService.delete_user(user_id)
        
        if error:
            return jsonify({'message': error}), 404 if 'not found' in error else 400
        
        return jsonify({
            'message': 'User deleted successfully'
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to delete user: {str(e)}'}), 500