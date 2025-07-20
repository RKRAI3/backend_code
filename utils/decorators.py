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
