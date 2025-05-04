from flask import Blueprint, jsonify, request
from flask_restx import Resource, fields, Namespace
from nba_api.stats.endpoints import TeamGameLogs
from nba_api.stats.library.parameters import SeasonAll

teams_bp = Blueprint("teams", __name__)
api = Namespace("teams", description="Team related operations")

# Define models for Swagger documentation
game_log_model = api.model(
    "GameLog",
    {
        "game_id": fields.String(description="Unique identifier for the game"),
        "game_date": fields.String(description="Date of the game"),
        "matchup": fields.String(description="Teams playing in the game"),
        "result": fields.String(description="Game result (W/L)"),
        "points": fields.Integer(description="Points scored"),
        "field_goals_made": fields.Integer(description="Field goals made"),
        "field_goals_attempted": fields.Integer(description="Field goals attempted"),
        "field_goal_percentage": fields.Float(description="Field goal percentage"),
        "three_pointers_made": fields.Integer(description="Three pointers made"),
        "three_pointers_attempted": fields.Integer(
            description="Three pointers attempted"
        ),
        "three_point_percentage": fields.Float(description="Three point percentage"),
        "free_throws_made": fields.Integer(description="Free throws made"),
        "free_throws_attempted": fields.Integer(description="Free throws attempted"),
        "free_throw_percentage": fields.Float(description="Free throw percentage"),
        "offensive_rebounds": fields.Integer(description="Offensive rebounds"),
        "defensive_rebounds": fields.Integer(description="Defensive rebounds"),
        "total_rebounds": fields.Integer(description="Total rebounds"),
        "assists": fields.Integer(description="Assists"),
        "turnovers": fields.Integer(description="Turnovers"),
        "steals": fields.Integer(description="Steals"),
        "blocks": fields.Integer(description="Blocks"),
        "blocks_against": fields.Integer(description="Blocks against"),
        "personal_fouls": fields.Integer(description="Personal fouls"),
        "personal_fouls_drawn": fields.Integer(description="Personal fouls drawn"),
        "plus_minus": fields.Integer(description="Plus/minus rating"),
    },
)

team_games_response = api.model(
    "TeamGamesResponse",
    {
        "team_id": fields.Integer(description="Team ID"),
        "season": fields.String(description="NBA season"),
        "games_played": fields.Integer(description="Number of games played"),
        "games": fields.List(fields.Nested(game_log_model)),
    },
)


@api.route("/teams/<int:team_id>/games")
class TeamGames(Resource):
    @api.doc(
        "get_team_games",
        params={"season": "NBA season (e.g., 2023-24). Defaults to current season."},
    )
    @api.response(200, "Success", team_games_response)
    @api.response(500, "Internal Server Error")
    def get(self, team_id):
        """Get game logs for a specific team"""
        try:
            # Get season from query parameter, default to current season
            season = request.args.get("season", SeasonAll.current_season)

            # Get team's game logs for the specified season
            team_logs = TeamGameLogs(team_id_nullable=team_id, season_nullable=season)

            # Get the data as a dictionary
            data = team_logs.get_normalized_dict()

            # Extract relevant game data
            games = []
            for game in data["TeamGameLogs"]:
                game_data = {
                    "game_id": game["GAME_ID"],
                    "game_date": game["GAME_DATE"],
                    "matchup": game["MATCHUP"],
                    "result": game["WL"],
                    "points": game["PTS"],
                    "field_goals_made": game["FGM"],
                    "field_goals_attempted": game["FGA"],
                    "field_goal_percentage": game["FG_PCT"],
                    "three_pointers_made": game["FG3M"],
                    "three_pointers_attempted": game["FG3A"],
                    "three_point_percentage": game["FG3_PCT"],
                    "free_throws_made": game["FTM"],
                    "free_throws_attempted": game["FTA"],
                    "free_throw_percentage": game["FT_PCT"],
                    "offensive_rebounds": game["OREB"],
                    "defensive_rebounds": game["DREB"],
                    "total_rebounds": game["REB"],
                    "assists": game["AST"],
                    "turnovers": game["TOV"],
                    "steals": game["STL"],
                    "blocks": game["BLK"],
                    "blocks_against": game["BLKA"],
                    "personal_fouls": game["PF"],
                    "personal_fouls_drawn": game["PFD"],
                    "plus_minus": game["PLUS_MINUS"],
                }
                games.append(game_data)

            return {
                "team_id": team_id,
                "season": season,
                "games_played": len(games),
                "games": games,
            }

        except Exception as e:
            return {"error": str(e)}, 500
