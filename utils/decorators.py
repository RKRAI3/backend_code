from functools import wraps
from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt
from models.user import User

def admin_required(f):
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        claims = get_jwt()
        if not claims.get('is_admin', False):
            return jsonify({'message': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return decorated_function


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
