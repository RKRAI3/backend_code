from flask import Blueprint, request, jsonify
from services.country_service import CountryService
from validators.schemas import CountryCreateSchema, CountryUpdateSchema
from utils.decorators import country_scope, validate_json
from models.user import SUPER_ADMIN

country_bp = Blueprint('countries', __name__)


@country_bp.route('/', methods=['GET'])
@country_scope(roles=[SUPER_ADMIN])
def get_countries(country_id):
    """List all countries (Super admin only)"""
    try:
        include_inactive = request.args.get('include_inactive', 'true').lower() == 'true'
        countries = CountryService.get_all_countries(include_inactive)
        return jsonify({
            'status': True,
            'message': 'Countries retrieved successfully',
            'data': [c.to_dict() for c in countries]
        }), 200
    except Exception as e:
        return jsonify({'status': False, 'message': f'Failed to retrieve countries: {str(e)}'}), 500


@country_bp.route('/', methods=['POST'])
@country_scope(roles=[SUPER_ADMIN])
@validate_json(CountryCreateSchema)
def create_country(validated_data, country_id):
    """Create a country (Super admin only)"""
    try:
        country, error = CountryService.create_country(validated_data)
        if error:
            return jsonify({'status': False, 'message': error}), 400
        return jsonify({
            'status': True,
            'message': 'Country created successfully',
            'data': country.to_dict()
        }), 201
    except Exception as e:
        return jsonify({'status': False, 'message': f'Failed to create country: {str(e)}'}), 500


@country_bp.route('/<string:target_id>', methods=['GET'])
@country_scope(roles=[SUPER_ADMIN])
def get_country(target_id, country_id):
    """Get country by ID (Super admin only)"""
    country = CountryService.get_country_by_id(target_id)
    if not country:
        return jsonify({'status': False, 'message': 'Country not found'}), 404
    return jsonify({'status': True, 'data': country.to_dict()}), 200


@country_bp.route('/<string:target_id>', methods=['PUT'])
@country_scope(roles=[SUPER_ADMIN])
@validate_json(CountryUpdateSchema)
def update_country(validated_data, target_id, country_id):
    """Update country configuration (Super admin only)"""
    try:
        country, error = CountryService.update_country(target_id, validated_data)
        if error:
            return jsonify({'status': False, 'message': error}), 404 if 'not found' in error else 400
        return jsonify({
            'status': True,
            'message': 'Country updated successfully',
            'data': country.to_dict()
        }), 200
    except Exception as e:
        return jsonify({'status': False, 'message': f'Failed to update country: {str(e)}'}), 500


@country_bp.route('/<string:target_id>', methods=['DELETE'])
@country_scope(roles=[SUPER_ADMIN])
def deactivate_country(target_id, country_id):
    """Deactivate a country (Super admin only). Data is kept."""
    try:
        success, error = CountryService.deactivate_country(target_id)
        if error:
            return jsonify({'status': False, 'message': error}), 404 if 'not found' in error else 400
        return jsonify({'status': True, 'message': 'Country deactivated successfully'}), 200
    except Exception as e:
        return jsonify({'status': False, 'message': f'Failed to deactivate country: {str(e)}'}), 500
