from models.user import User
from app import db
from sqlalchemy.exc import IntegrityError

class UserService:
    @staticmethod
    def create_user(user_data, created_by_id=None):
        """Create a new user"""
        try:
            user = User(
                user_name=user_data['user_name'],
                email=user_data['email'],
                password=user_data['password'],
                is_admin=user_data.get('is_admin', False),
                created_by=created_by_id
            )
            
            db.session.add(user)
            db.session.commit()
            return user, None
            
        except IntegrityError:
            db.session.rollback()
            return None, "Email already exists"
        except Exception as e:
            db.session.rollback()
            return None, str(e)
    
    @staticmethod
    def get_all_users(page=1, per_page=10):
        """Get all active users with pagination"""
        users = User.query.filter_by(deleted_at=None).paginate(
            page=page, per_page=per_page, error_out=False
        )
        return users
    
    @staticmethod
    def get_user_by_id(user_id):
        """Get user by ID"""
        return User.query.filter_by(user_id=user_id, deleted_at=None).first()
    
    @staticmethod
    def update_user(user_id, update_data):
        """Update user information"""
        try:
            user = User.query.filter_by(user_id=user_id, deleted_at=None).first()
            if not user:
                return None, "User not found"
            
            for key, value in update_data.items():
                if value is not None and hasattr(user, key):
                    setattr(user, key, value)
            
            db.session.commit()
            return user, None
            
        except IntegrityError:
            db.session.rollback()
            return None, "Email already exists"
        except Exception as e:
            db.session.rollback()
            return None, str(e)
    
    @staticmethod
    def delete_user(user_id):
        """Soft delete user"""
        try:
            user = User.query.filter_by(user_id=user_id, deleted_at=None).first()
            if not user:
                return False, "User not found"
            
            user.soft_delete()
            db.session.commit()
            return True, None
            
        except Exception as e:
            db.session.rollback()
            return False, str(e)
