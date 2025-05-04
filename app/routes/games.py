from flask import Blueprint, jsonify
from flask_restx import Resource, fields, Namespace
from app.services.game_service import get_today_games

games_bp = Blueprint("games", __name__)
api = Namespace("games", description="Game related operations")

# Define models for Swagger documentation
game_model = api.model(
    "Game",
    {
        "game_date": fields.String(description="Date of the game"),
        "game_status": fields.String(description="Current status of the game"),
        "home_team": fields.Nested(
            api.model(
                "Team",
                {
                    "id": fields.Integer(description="Team ID"),
                    "abbreviation": fields.String(description="Team abbreviation"),
                    "arena": fields.String(description="Arena name"),
                },
            )
        ),
        "visitor_team": fields.Nested(
            api.model(
                "Team",
                {
                    "id": fields.Integer(description="Team ID"),
                    "abbreviation": fields.String(description="Team abbreviation"),
                },
            )
        ),
        "live_period": fields.String(description="Current period of the game"),
        "live_period_time_bcast": fields.String(
            description="Time remaining in the current period"
        ),
    },
)


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
