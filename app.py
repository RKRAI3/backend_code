from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from datetime import timedelta
from environment import SECRET_KEY, DATABASE_URL, JWT_SECRET_KEY, ADMIN_NAME, ADMIN_ID, PASSWORD, SQLALCHEMY_TRACK_MODIFICATIONS, TOKEN_EXPIRY


# Initialize extensions
db = SQLAlchemy()
jwt = JWTManager()
bcrypt = Bcrypt()

def create_app():
    app = Flask(__name__)
    CORS(app, resources={r"/api/*": {"origins": "http://localhost:5173/"}})
    # Configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_recycle': 300,
        'pool_pre_ping': True,
        'pool_size': 10,
        'max_overflow': 20
    }
    app.config['JWT_SECRET_KEY'] = JWT_SECRET_KEY
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=int(TOKEN_EXPIRY))
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)
    
    # Initialize extensions with app
    db.init_app(app)
    jwt.init_app(app)
    bcrypt.init_app(app)
    CORS(app)
    
    # Register blueprints
    from controllers.auth_controller import auth_bp
    from controllers.user_controller import user_bp
    from controllers.product_controller import product_bp
    from controllers.receipt_controller import receipt_bp
    from controllers.receipt_item_controller import receipt_item_bp
    from controllers.dashboard_controller import dashboard_bp
    @app.route("/")
    def home():
        return "Welcome!"
    app.register_blueprint(receipt_item_bp, url_prefix='/api/receipt_items')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(user_bp, url_prefix='/api/users')
    app.register_blueprint(product_bp, url_prefix='/api/products')
    app.register_blueprint(receipt_bp, url_prefix='/api/receipts')
    app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
    
    
    # Create tables
    with app.app_context():
        db.create_all()
        
        # Create default admin user if not exists
        from models.user import User
        admin = User.query.filter_by(email=ADMIN_ID).first()
        if not admin:
            admin_user = User(
                user_name=ADMIN_NAME,
                email=ADMIN_ID,
                password=PASSWORD,
                is_admin=True
            )
            db.session.add(admin_user)
            db.session.commit()
    
    return app
