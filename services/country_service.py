from models.country import Country
from app import db
from sqlalchemy.exc import IntegrityError


class CountryService:
    @staticmethod
    def _apply(country, data):
        for key, value in data.items():
            if value is None or not hasattr(country, key):
                continue
            if key == 'alert_emails':
                value = ','.join(value)
            setattr(country, key, value)

    @staticmethod
    def create_country(country_data):
        """Create a new country configuration"""
        try:
            country = Country()
            CountryService._apply(country, country_data)
            db.session.add(country)
            db.session.commit()
            return country, None
        except IntegrityError:
            db.session.rollback()
            return None, f"Country with code {country_data['code']} already exists"
        except Exception as e:
            db.session.rollback()
            return None, str(e)

    @staticmethod
    def get_all_countries(include_inactive=True):
        query = Country.query
        if not include_inactive:
            query = query.filter_by(is_active=True)
        return query.order_by(Country.name).all()

    @staticmethod
    def get_country_by_id(country_id):
        return Country.query.get(country_id)

    @staticmethod
    def update_country(country_id, update_data):
        """Update country configuration"""
        try:
            country = Country.query.get(country_id)
            if not country:
                return None, "Country not found"
            CountryService._apply(country, update_data)
            db.session.commit()
            return country, None
        except Exception as e:
            db.session.rollback()
            return None, str(e)

    @staticmethod
    def deactivate_country(country_id):
        """Deactivate a country; its users can no longer log in to work"""
        try:
            country = Country.query.get(country_id)
            if not country:
                return False, "Country not found"
            country.is_active = False
            db.session.commit()
            return True, None
        except Exception as e:
            db.session.rollback()
            return False, str(e)
