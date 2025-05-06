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
            "season_type": "Comma-separated list of game types (Regular Season, Playoffs, Pre Season, All Star). Defaults to Regular Season."
        },
    )
    @api.response(200, "Success", team_games_response)
    @api.response(500, "Internal Server Error")
    def get(self, team_id):
        """Get game logs for a specific team"""
        try:
            # Get season from query parameter, default to current season
            season = request.args.get("season", SeasonAll.current_season)
            season_types = request.args.get("season_type", "Regular Season").split(",")
            
            # Get team's game logs for each season type and combine them
            all_games = []
            for season_type in season_types:
                season_type = season_type.strip()  # Remove any whitespace
                try:
                    team_logs = TeamGameLogs(
                        team_id_nullable=team_id,
                        season_nullable=season,
                        season_type_nullable=season_type
                    )
                    
                    # Get the data as a dictionary
                    data = team_logs.get_normalized_dict()
                    
                    # Extract relevant game data
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
                            "season_type": season_type  # Add season type to each game
                        }
                        all_games.append(game_data)
                except Exception as e:
                    print(f"Error fetching {season_type} games: {str(e)}")
                    continue
            
            # Sort games by date in reverse order (most recent first)
            all_games.sort(key=lambda x: x["game_date"], reverse=True)
            
            return {
                "team_id": team_id,
                "season": season,
                "season_types": season_types,
                "games_played": len(all_games),
                "games": all_games
            }
            
        except Exception as e:
            return {"error": str(e)}, 500
