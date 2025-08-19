from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, JWTManager
from models.user import User
from app import db

class AuthService:
    @staticmethod
    def authenticate_user(email, password):
        """Authenticate user with email and password"""
        user = User.query.filter_by(email=email, deleted_at=None).first()
        if user and user.verify_password(password):
            return user
        return None
    
    @staticmethod
    def generate_tokens(user):
        """Generate access and refresh tokens for user"""
        additional_claims = {
            'user_id': user.user_id,
            'is_admin': user.is_admin,
            'email': user.email
        }
        
        access_token = create_access_token(
            identity=str(user.user_id),
            additional_claims=additional_claims
        )
        # refresh_token = create_refresh_token(identity=user.user_id)
        refresh_token =None
        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': user.to_dict()
        }
    
    @staticmethod
    def refresh_access_token():
        """Generate new access token from refresh token"""
        current_user_id = get_jwt_identity()
        user = User.query.filter_by(user_id=current_user_id, deleted_at=None).first()
        
        if not user:
            return None
        
        additional_claims = {
            'user_id': user.user_id,
            'is_admin': user.is_admin,
            'email': user.email
        }
        
        new_access_token = create_access_token(
            identity=user.user_id,
            additional_claims=additional_claims
        )
        
        return {'access_token': new_access_token}

