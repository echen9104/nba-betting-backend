from flask import Blueprint, jsonify
from flask_restx import Resource, Namespace
from app.services.game_service import get_today_games
from app.models.games_model import api, game_model

games_bp = Blueprint("games", __name__)

@api.route("/today")
class TodayGames(Resource):
    @api.doc("get_today_games")
    @api.response(200, "Success", game_model)
    @api.response(500, "Internal Server Error")
    def get(self):
        """Get today's NBA games"""
        try:
            games_data = get_today_games()
            return games_data
        except Exception as e:
            return {"error": str(e)}, 500
