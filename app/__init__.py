from flask import Flask
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    CORS(app)  # Enable CORS for all routes
    
    # Register blueprints
    from app.routes import games_bp
    app.register_blueprint(games_bp)
    
    return app 