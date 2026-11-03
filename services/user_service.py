from models.user import User, SUPER_ADMIN, COUNTRY_ADMIN, STAFF
from models.country import Country
from app import db
from sqlalchemy.exc import IntegrityError

class UserService:
    @staticmethod
    def resolve_role(data, default=STAFF):
        """Role from the payload; falls back to the legacy is_admin flag"""
        if data.get('role'):
            return data['role']
        if data.get('is_admin') is not None:
            return COUNTRY_ADMIN if data['is_admin'] else STAFF
        return default

    @staticmethod
    def check_assignment(actor, role, country_id):
        """Validate that `actor` may give a user this role/country. Returns an error or None"""
        if actor is not None and not actor.is_super_admin:
            if role == SUPER_ADMIN:
                return "Only a super admin can create super admins"
            if country_id != actor.country_id:
                return "You can only manage users of your own country"
        if role == SUPER_ADMIN:
            return None
        if not country_id:
            return "country_id is required for this role"
        if not Country.query.get(country_id):
            return "Country not found"
        return None

    @staticmethod
    def create_user(user_data, actor=None, created_by_id=None):
        """Create a new user. `actor` is the admin creating it (None for self-registration)"""
        try:
            role = UserService.resolve_role(user_data)
            country_id = None if role == SUPER_ADMIN else user_data.get('country_id')
            if actor is not None and not actor.is_super_admin:
                country_id = country_id or actor.country_id
            error = UserService.check_assignment(actor, role, country_id)
            if error:
                return None, error
            user = User(
                user_name=user_data['user_name'],
                email=user_data['email'],
                password=user_data['password'],
                role=role,
                country_id=country_id,
                created_by=created_by_id
            )

            db.session.add(user)
            db.session.commit()
            return user, None

        except IntegrityError as e:
            db.session.rollback()
            return None, "Email already exists"
        except Exception as e:
            db.session.rollback()
            return None, str(e)

    @staticmethod
    def get_all_users(page=1, per_page=10, country_id=None):
        """Get all active users with pagination, optionally limited to one country"""
        query = User.query.filter_by(deleted_at=None)
        if country_id:
            query = query.filter_by(country_id=country_id)
        users = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        return users

    @staticmethod
    def get_user_by_id(user_id, country_id=None):
        """Get user by ID, optionally limited to one country"""
        query = User.query.filter_by(user_id=user_id, deleted_at=None)
        if country_id:
            query = query.filter_by(country_id=country_id)
        return query.first()

    @staticmethod
    def update_user(user_id, update_data, actor=None, country_id=None):
        """Update user information"""
        try:
            user = UserService.get_user_by_id(user_id, country_id)
            if not user:
                return None, "User not found"

            role = UserService.resolve_role(update_data, default=user.role)
            new_country_id = None if role == SUPER_ADMIN else (update_data.get('country_id') or user.country_id)
            error = UserService.check_assignment(actor, role, new_country_id)
            if error:
                return None, error
            user.role = role
            user.country_id = new_country_id

            for key in ('user_name', 'email'):
                if update_data.get(key) is not None:
                    setattr(user, key, update_data[key])

            db.session.commit()
            return user, None

        except IntegrityError:
            db.session.rollback()
            return None, "Email already exists"
        except Exception as e:
            db.session.rollback()
            return None, str(e)

    @staticmethod
    def delete_user(user_id, country_id=None):
        """Soft delete user"""
        try:
            user = UserService.get_user_by_id(user_id, country_id)
            if not user:
                return False, "User not found"

            user.soft_delete()
            db.session.commit()
            return True, None

        except Exception as e:
            db.session.rollback()
            return False, str(e)
