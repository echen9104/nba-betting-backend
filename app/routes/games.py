from flask import Blueprint, jsonify
from app.services.game_service import get_today_games

games_bp = Blueprint('games', __name__)

@games_bp.route('/games/today', methods=['GET'])
def today_games():
    try:
        games_data = get_today_games()
        return jsonify(games_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500 