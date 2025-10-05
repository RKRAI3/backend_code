from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.auth_service import AuthService
from services.user_service import UserService
from validators.schemas import LoginSchema, UserCreateSchema
from utils.decorators import validate_json
from pydantic import ValidationError

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
@validate_json(LoginSchema)
def login(validated_data):
    """User login endpoint"""
    try:
        email = validated_data['email']
        password = validated_data['password']
        print(f"Attempting login for email: {email} and password: {password}")
        user = AuthService.authenticate_user(email, password)
        if not user:
            return jsonify({'message': 'Invalid email or password'}), 401
        
        tokens = AuthService.generate_tokens(user)
        
        return jsonify({
            'message': 'Login successful',
            'data': tokens
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Login failed: {str(e)}'}), 500

@auth_bp.route('/register', methods=['POST'])
@validate_json(UserCreateSchema)
def register(validated_data):
    """User registration endpoint"""
    try:
        user, error = UserService.create_user(validated_data)
        if error:
            return jsonify({'message': error}), 400
        
        tokens = AuthService.generate_tokens(user)
        return jsonify({
            'message': 'Registration successful',
            'data': tokens
        }), 201
        
    except Exception as e:
        return jsonify({'message': f'Registration failed: {str(e)}'}), 500

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token endpoint"""
    try:
        tokens = AuthService.refresh_access_token()
        if not tokens:
            return jsonify({'message': 'User not found'}), 404
        
        return jsonify({
            'message': 'Token refreshed successfully',
            'data': tokens
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Token refresh failed: {str(e)}'}), 500

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current user information"""
    try:
        current_user_id = get_jwt_identity()
        user = UserService.get_user_by_id(current_user_id)
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        return jsonify({
            'message': 'User information retrieved successfully',
            'data': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Failed to get user information: {str(e)}'}), 500
