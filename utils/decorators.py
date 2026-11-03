from functools import wraps
from flask import jsonify, request, g
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from models.user import User, SUPER_ADMIN
from models.country import Country

def admin_required(f):
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        claims = get_jwt()
        if not claims.get('is_admin', False):
            return jsonify({'message': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return decorated_function


def country_scope(required=False, roles=None):
    """Resolve which country the request acts on and pass it to the view as `country_id`.

    Country users are always pinned to their own country. A super admin picks one with
    `country_id` in the query string or JSON body; when `required` is False and none is
    given, `country_id` is None, meaning all countries.
    The logged-in user is loaded from the DB (not the token) and exposed as `g.current_user`.
    """
    def decorator(f):
        @wraps(f)
        @jwt_required()
        def decorated_function(*args, **kwargs):
            user = User.query.filter_by(user_id=get_jwt_identity(), deleted_at=None).first()
            if not user:
                return jsonify({'status': False, 'message': 'User not found'}), 401
            if roles and user.role not in roles:
                return jsonify({'status': False, 'message': 'You do not have permission for this action'}), 403

            if user.role == SUPER_ADMIN:
                body = request.get_json(silent=True)
                country_id = request.args.get('country_id') or (body.get('country_id') if isinstance(body, dict) else None)
                if country_id and not Country.query.get(country_id):
                    return jsonify({'status': False, 'message': 'Country not found'}), 404
                if required and not country_id:
                    return jsonify({'status': False, 'message': 'country_id is required'}), 400
            else:
                if not user.country or not user.country.is_active:
                    return jsonify({'status': False, 'message': 'Your account is not assigned to an active country'}), 403
                country_id = user.country_id

            g.current_user = user
            return f(*args, country_id=country_id, **kwargs)
        return decorated_function
    return decorator


def validate_json(schema):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from flask import request
            try:
                # Parse and validate JSON data
                json_data = request.get_json()
                if not json_data:
                    return jsonify({'message': 'No JSON data provided'}), 400
                
                # Validate using Pydantic schema
                validated_data = schema(**json_data)
                # Pass validated data to the route function
                return f(validated_data.dict(), *args, **kwargs)
                
            except Exception as e:
                return jsonify({'message': f'Validation error: {str(e)}'}), 400
        return decorated_function
    return decorator


def validate_create_json(schema):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from flask import request
            try:
                # Parse and validate JSON data
                json_data = request.get_json()
                for rcpt_itm in json_data['items']:
                    if 'updated_price' in rcpt_itm:
                        rcpt_itm['vendor_price'] = rcpt_itm.pop('updated_price')
                    # Add new key 'free'
                    rcpt_itm['is_free'] = False  # ✅ This line is now valid
 
                #     rcpt_itm["vendor_price"] = rcpt_itm.pop("updated_price")    
                # rcpt_itm['free'] = True
                json_data['package'] = None    
                json_data['package_amt'] = 0            
                if not json_data:
                    return jsonify({'message': 'No JSON data provided'}), 400
                # Validate using Pydantic schema
                validated_data = schema(**json_data)
                # Pass validated data to the route function
                return f(validated_data.dict(), *args, **kwargs)
                
            except Exception as e:
                return jsonify({'message': f'Validation error: {str(e)}'}), 400
        return decorated_function
    return decorator
