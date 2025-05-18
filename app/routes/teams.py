from flask import Blueprint, jsonify, request
from flask_restx import Resource, Namespace
from nba_api.stats.endpoints import TeamGameLogs, BoxScoreTraditionalV2
from nba_api.stats.library.parameters import SeasonAll, SeasonType
from app.models.teams_model import api, game_log_model, team_games_response
import re
import logging
import traceback
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import lru_cache
import threading

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

teams_bp = Blueprint("teams", __name__)

# Team abbreviation to ID mapping
TEAM_ABBREVIATIONS = {
    'ATL': 1610612737, 'BOS': 1610612738, 'BKN': 1610612751, 'CHA': 1610612766,
    'CHI': 1610612741, 'CLE': 1610612739, 'DAL': 1610612742, 'DEN': 1610612743,
    'DET': 1610612765, 'GSW': 1610612744, 'HOU': 1610612745, 'IND': 1610612754,
    'LAC': 1610612746, 'LAL': 1610612747, 'MEM': 1610612763, 'MIA': 1610612748,
    'MIL': 1610612749, 'MIN': 1610612750, 'NOP': 1610612740, 'NYK': 1610612752,
    'OKC': 1610612760, 'ORL': 1610612753, 'PHI': 1610612755, 'PHX': 1610612756,
    'POR': 1610612757, 'SAC': 1610612758, 'SAS': 1610612759, 'TOR': 1610612761,
    'UTA': 1610612762, 'WAS': 1610612764
}

# Cache for team game logs
@lru_cache(maxsize=128)
def get_cached_team_logs(team_id, season, season_type):
    """Get cached team game logs"""
    return TeamGameLogs(
        team_id_nullable=team_id,
        season_nullable=season,
        season_type_nullable=season_type
    ).get_normalized_dict()

# Cache for box scores
@lru_cache(maxsize=256)
def get_cached_box_score(game_id):
    """Get cached box score data"""
    return BoxScoreTraditionalV2(game_id=game_id).get_normalized_dict()

def process_game(game, team1_id, team2_id, season_type):
    """Process a single game and return its data"""
    try:
        game_id = game["GAME_ID"]
        logger.info(f"Processing game {game_id}")
        
        # Get box score data from cache
        box_score_data = get_cached_box_score(game_id)
        
        # Get stats for both teams
        team1_stats = None
        team2_stats = None
        for team in box_score_data["TeamStats"]:
            if team["TEAM_ID"] == team1_id:
                team1_stats = {
                    "points": team["PTS"],
                    "field_goals_made": team["FGM"],
                    "field_goals_attempted": team["FGA"],
                    "field_goal_percentage": team["FG_PCT"],
                    "three_pointers_made": team["FG3M"],
                    "three_pointers_attempted": team["FG3A"],
                    "three_point_percentage": team["FG3_PCT"],
                    "free_throws_made": team["FTM"],
                    "free_throws_attempted": team["FTA"],
                    "free_throw_percentage": team["FT_PCT"],
                    "offensive_rebounds": team["OREB"],
                    "defensive_rebounds": team["DREB"],
                    "total_rebounds": team["REB"],
                    "assists": team["AST"],
                    "turnovers": team.get("TOV", 0),
                    "steals": team.get("STL", 0),
                    "blocks": team.get("BLK", 0),
                    "blocks_against": team.get("BLKA", 0),
                    "personal_fouls": team.get("PF", 0),
                    "personal_fouls_drawn": team.get("PFD", 0),
                    "plus_minus": team.get("PLUS_MINUS", 0)
                }
            elif team["TEAM_ID"] == team2_id:
                team2_stats = {
                    "points": team["PTS"],
                    "field_goals_made": team["FGM"],
                    "field_goals_attempted": team["FGA"],
                    "field_goal_percentage": team["FG_PCT"],
                    "three_pointers_made": team["FG3M"],
                    "three_pointers_attempted": team["FG3A"],
                    "three_point_percentage": team["FG3_PCT"],
                    "free_throws_made": team["FTM"],
                    "free_throws_attempted": team["FTA"],
                    "free_throw_percentage": team["FT_PCT"],
                    "offensive_rebounds": team["OREB"],
                    "defensive_rebounds": team["DREB"],
                    "total_rebounds": team["REB"],
                    "assists": team["AST"],
                    "turnovers": team.get("TOV", 0),
                    "steals": team.get("STL", 0),
                    "blocks": team.get("BLK", 0),
                    "blocks_against": team.get("BLKA", 0),
                    "personal_fouls": team.get("PF", 0),
                    "personal_fouls_drawn": team.get("PFD", 0),
                    "plus_minus": team.get("PLUS_MINUS", 0)
                }
        
        if team1_stats and team2_stats:
            return {
                "game_id": game["GAME_ID"],
                "game_date": game["GAME_DATE"],
                "matchup": game["MATCHUP"],
                "result": game["WL"],
                "team1_stats": team1_stats,
                "team2_stats": team2_stats,
                "season_type": season_type
            }
        return None
    except Exception as e:
        logger.error(f"Error processing game {game.get('GAME_ID', 'unknown')}: {str(e)}")
        return None

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

@api.route("/matchups")
class TeamMatchups(Resource):
    @api.doc(
        "get_team_matchups",
        params={
            "team1": "First team abbreviation (e.g., BOS)",
            "team2": "Second team abbreviation (e.g., NYK)",
            "season": "NBA season (e.g., 2023-24). Defaults to current season.",
            "season_type": "Comma-separated list of game types (Regular Season, Playoffs, Pre Season, All Star). Defaults to Regular Season."
        },
    )
    @api.response(200, "Success")
    @api.response(400, "Invalid team abbreviation")
    @api.response(500, "Internal Server Error")
    def get(self):
        """Get matchup data between two teams"""
        try:
            # Get team abbreviations from query parameters
            team1 = request.args.get("team1", "").upper()
            team2 = request.args.get("team2", "").upper()
            
            logger.info(f"Received request for matchup between {team1} and {team2}")
            
            if not team1 or not team2:
                logger.error("Missing team parameters")
                return {"error": "Both team1 and team2 parameters are required"}, 400
                
            if team1 not in TEAM_ABBREVIATIONS or team2 not in TEAM_ABBREVIATIONS:
                logger.error(f"Invalid team abbreviation. team1: {team1}, team2: {team2}")
                return {"error": "Invalid team abbreviation. Use standard NBA team abbreviations (e.g., BOS, NYK)"}, 400
                
            team1_id = TEAM_ABBREVIATIONS[team1]
            team2_id = TEAM_ABBREVIATIONS[team2]
            logger.info(f"Team IDs - {team1}: {team1_id}, {team2}: {team2_id}")
            
            # Get season from query parameter, default to current season
            season = request.args.get("season", SeasonAll.current_season)
            season_types = request.args.get("season_type", "Regular Season").split(",")
            logger.info(f"Fetching data for season {season} and types {season_types}")
            
            # Get games for both teams
            all_games = []
            for season_type in season_types:
                season_type = season_type.strip()
                try:
                    logger.info(f"Fetching {season_type} games for {team1}")
                    # Get team1's games from cache
                    team1_data = get_cached_team_logs(team1_id, season, season_type)
                    logger.info(f"Found {len(team1_data['TeamGameLogs'])} total games for {team1} in {season_type}")
                    
                    # Filter for games against team2
                    matchup_games = []
                    for game in team1_data["TeamGameLogs"]:
                        matchup = game["MATCHUP"]
                        if team2 in matchup:
                            matchup_games.append(game)
                    
                    logger.info(f"Found {len(matchup_games)} matchup games in {season_type}")
                    
                    # Process games in parallel
                    with ThreadPoolExecutor(max_workers=5) as executor:
                        future_to_game = {
                            executor.submit(process_game, game, team1_id, team2_id, season_type): game 
                            for game in matchup_games
                        }
                        
                        for future in as_completed(future_to_game):
                            game_data = future.result()
                            if game_data:
                                all_games.append(game_data)
                    
                except Exception as e:
                    logger.error(f"Error fetching {season_type} games: {str(e)}")
                    continue
            
            # Sort games by date in reverse order (most recent first)
            all_games.sort(key=lambda x: x["game_date"], reverse=True)
            logger.info(f"Total games found: {len(all_games)}")
            
            return {
                "team1": team1,
                "team2": team2,
                "season": season,
                "season_types": season_types,
                "games_played": len(all_games),
                "games": all_games
            }
            
        except Exception as e:
            logger.error(f"Error in get_team_matchups: {str(e)}")
            return {"error": str(e)}, 500
