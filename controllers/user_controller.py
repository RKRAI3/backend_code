from flask import Blueprint, request, jsonify, g
from services.user_service import UserService
from validators.schemas import UserCreateSchema, UserUpdateSchema
from utils.decorators import country_scope, validate_json
from models.user import SUPER_ADMIN, COUNTRY_ADMIN

ADMIN_ROLES = [SUPER_ADMIN, COUNTRY_ADMIN]

user_bp = Blueprint('users', __name__)

@user_bp.route('/users', methods=['GET'])
@country_scope()
def get_users(country_id):
    """Get all users with pagination"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 10, type=int), 100)
        
        users_paginated = UserService.get_all_users(page, per_page, country_id)
        
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

@user_bp.route('/createuser', methods=['POST'])
@country_scope(roles=ADMIN_ROLES)
@validate_json(UserCreateSchema)
def create_user(validated_data, country_id):
    """Create a new user (Admin only). Country admins can only create users in their own country."""
    try:
        actor = g.current_user
        user, error = UserService.create_user(validated_data, actor=actor, created_by_id=actor.user_id)
        if error:
            return jsonify({'message': error}), 400
        return jsonify({
            'message': 'User created successfully',
            'data': user.to_dict()
        }), 201
    except Exception as e:
        return jsonify({'message': f'Failed to create user: {str(e)}'}), 500

@user_bp.route('/<string:user_id>', methods=['GET'])
@country_scope()
def get_user(user_id, country_id):
    """Get user by ID"""
    try:
        user = UserService.get_user_by_id(user_id, country_id)
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        return jsonify({
            'message': 'User retrieved successfully',
            'data': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to retrieve user: {str(e)}'}), 500

@user_bp.route('/<string:user_id>', methods=['PUT'])
@country_scope(roles=ADMIN_ROLES)
@validate_json(UserUpdateSchema)
def update_user(validated_data, user_id, country_id):
    """Update user information (Admin only)"""
    try:
        # Super admins look the user up across all countries; country_id in the body is the new country
        scope = None if g.current_user.is_super_admin else country_id
        user, error = UserService.update_user(user_id, validated_data, actor=g.current_user, country_id=scope)
        
        if error:
            return jsonify({'message': error}), 400
        
        return jsonify({
            'message': 'User updated successfully',
            'data': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to update user: {str(e)}'}), 500

@user_bp.route('/<string:user_id>', methods=['DELETE'])
@country_scope(roles=ADMIN_ROLES)
def delete_user(user_id, country_id):
    """Delete user (Admin only)"""
    try:
        success, error = UserService.delete_user(user_id, country_id)
        
        if error:
            return jsonify({'message': error}), 404 if 'not found' in error else 400
        
        return jsonify({
            'message': 'User deleted successfully'
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to delete user: {str(e)}'}), 500