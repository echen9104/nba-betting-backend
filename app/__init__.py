from flask import Flask
from flask_cors import CORS
from flask_restx import Api

def create_app():
    app = Flask(__name__)
    CORS(app)  # Enable CORS for all routes
    
    # Initialize API
    api = Api(app, version='1.0', title='NBA API',
              description='A simple API for NBA data',
              doc='/swagger')
    
    # Register blueprints
    from app.routes import games_bp, players_bp, teams_bp
    app.register_blueprint(games_bp)
    app.register_blueprint(players_bp)
    app.register_blueprint(teams_bp)
    
    # Register API namespaces
    from app.routes.games import api as games_api
    from app.routes.players import api as players_api
    from app.routes.teams import api as teams_api
    
    api.add_namespace(games_api)
    api.add_namespace(players_api)
    api.add_namespace(teams_api)
    
    return app 