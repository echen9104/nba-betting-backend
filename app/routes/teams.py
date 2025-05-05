from flask import Blueprint, jsonify, request
from flask_restx import Resource, Namespace
from nba_api.stats.endpoints import TeamGameLogs
from nba_api.stats.library.parameters import SeasonAll, SeasonType
from app.models.teams_model import api, game_log_model, team_games_response

teams_bp = Blueprint("teams", __name__)

@api.route("/<int:team_id>/games")
class TeamGames(Resource):
    @api.doc(
        "get_team_games",
        params={
            "season": "NBA season (e.g., 2023-24). Defaults to current season.",
            "season_type": "Type of games to fetch (Regular Season, Playoffs, Pre Season, All Star). Defaults to Regular Season."
        },
    )
    @api.response(200, "Success", team_games_response)
    @api.response(500, "Internal Server Error")
    def get(self, team_id):
        """Get game logs for a specific team"""
        try:
            # Get season from query parameter, default to current season
            season = request.args.get("season", SeasonAll.current_season)
            season_type = request.args.get("season_type", "Regular Season")
            
            # Get team's game logs for the specified season and season type
            team_logs = TeamGameLogs(
                team_id_nullable=team_id,
                season_nullable=season,
                season_type_nullable=season_type
            )
            
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
                    "plus_minus": game["PLUS_MINUS"]
                }
                games.append(game_data)
            
            return {
                "team_id": team_id,
                "season": season,
                "season_type": season_type,
                "games_played": len(games),
                "games": games
            }
            
        except Exception as e:
            return {"error": str(e)}, 500
