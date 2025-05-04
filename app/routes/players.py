from flask import Blueprint, jsonify, request
from flask_restx import Resource, fields, Namespace
from nba_api.stats.endpoints import PlayerGameLogs, CommonPlayerInfo, CommonAllPlayers
from nba_api.stats.library.parameters import SeasonAll

players_bp = Blueprint("players", __name__)
api = Namespace("players", description="Player related operations")

# Define models for Swagger documentation
player_model = api.model(
    "Player",
    {
        "player_id": fields.Integer(description="Unique identifier for the player"),
        "name": fields.String(description="Player's full name"),
        "team": fields.String(description="Player's current team"),
        "position": fields.String(description="Player's position"),
        "jersey_number": fields.String(description="Player's jersey number"),
    },
)

player_search_response = api.model(
    "PlayerSearchResponse",
    {
        "count": fields.Integer(description="Number of players found"),
        "players": fields.List(fields.Nested(player_model)),
    },
)

player_info_model = api.model(
    "PlayerInfo",
    {
        "player_id": fields.Integer(description="Unique identifier for the player"),
        "name": fields.String(description="Player's full name"),
        "team": fields.String(description="Player's current team"),
        "position": fields.String(description="Player's position"),
        "height": fields.String(description="Player's height"),
        "weight": fields.String(description="Player's weight"),
        "birth_date": fields.String(description="Player's birth date"),
        "country": fields.String(description="Player's country of origin"),
        "jersey_number": fields.String(description="Player's jersey number"),
        "active": fields.Boolean(description="Whether the player is currently active"),
    },
)


@api.route("/search")
class PlayerSearch(Resource):
    @api.doc("search_players", params={"name": "Player name to search for"})
    @api.response(200, "Success", player_search_response)
    @api.response(400, "Bad Request")
    @api.response(404, "Not Found")
    @api.response(500, "Internal Server Error")
    def get(self):
        """Search for players by name"""
        try:
            name = request.args.get("name")
            if not name:
                return {"error": "Name parameter is required"}, 400

            # Get all players and filter by name
            all_players = CommonAllPlayers()
            data = all_players.get_normalized_dict()

            # Filter players by name
            matching_players = [
                player
                for player in data["CommonAllPlayers"]
                if name.lower() in f"{player['DISPLAY_FIRST_LAST']}".lower()
            ]

            if not matching_players:
                return {"error": "No players found"}, 404

            players = []
            for player in matching_players:
                players.append(
                    {
                        "player_id": player["PERSON_ID"],
                        "name": player["DISPLAY_FIRST_LAST"],
                        "team": player["TEAM_CITY"] + " " + player["TEAM_NAME"],
                        "position": player.get("POSITION", "N/A"),
                        "jersey_number": player.get("JERSEY", "N/A"),
                    }
                )

            return {"count": len(players), "players": players}

        except Exception as e:
            return {"error": str(e)}, 500


@api.route("/<int:player_id>")
class PlayerInfo(Resource):
    @api.doc("get_player_info")
    @api.response(200, "Success", player_info_model)
    @api.response(404, "Player Not Found")
    @api.response(500, "Internal Server Error")
    def get(self, player_id):
        """Get detailed information about a specific player"""
        try:
            player_info = CommonPlayerInfo(player_id=player_id)
            data = player_info.get_normalized_dict()

            if not data["CommonPlayerInfo"]:
                return {"error": "Player not found"}, 404

            player = data["CommonPlayerInfo"][0]
            return {
                "player_id": player["PERSON_ID"],
                "name": player["DISPLAY_FIRST_LAST"],
                "team": player["TEAM_CITY"] + " " + player["TEAM_NAME"],
                "position": player.get("POSITION", "N/A"),
                "height": player.get("HEIGHT", "N/A"),
                "weight": player.get("WEIGHT", "N/A"),
                "birth_date": player.get("BIRTHDATE", "N/A"),
                "country": player.get("COUNTRY", "N/A"),
                "jersey_number": player.get("JERSEY", "N/A"),
                "active": player.get("ROSTERSTATUS", "N/A") == "ACTIVE",
            }

        except Exception as e:
            return {"error": str(e)}, 500


@api.route("/<int:player_id>/stats")
class PlayerStats(Resource):
    @api.doc(
        "get_player_stats",
        params={"season": "NBA season (e.g., 2023-24). Defaults to current season."},
    )
    @api.response(200, "Success")
    @api.response(404, "Player Not Found")
    @api.response(500, "Internal Server Error")
    def get(self, player_id):
        """Get game statistics for a specific player"""
        try:
            season = request.args.get("season", SeasonAll.current_season)

            player_logs = PlayerGameLogs(
                player_id_nullable=player_id, season_nullable=season
            )
            data = player_logs.get_normalized_dict()

            if not data["PlayerGameLogs"]:
                return {"error": "No stats found for this player"}, 404

            stats = []
            for game in data["PlayerGameLogs"]:
                stats.append(
                    {
                        "game_id": game["GAME_ID"],
                        "game_date": game["GAME_DATE"],
                        "matchup": game["MATCHUP"],
                        "result": game["WL"],
                        "minutes": game["MIN"],
                        "points": game["PTS"],
                        "rebounds": game["REB"],
                        "assists": game["AST"],
                        "steals": game["STL"],
                        "blocks": game["BLK"],
                        "field_goals_made": game["FGM"],
                        "field_goals_attempted": game["FGA"],
                        "three_pointers_made": game["FG3M"],
                        "three_pointers_attempted": game["FG3A"],
                        "free_throws_made": game["FTM"],
                        "free_throws_attempted": game["FTA"],
                        "turnovers": game["TOV"],
                        "plus_minus": game["PLUS_MINUS"],
                    }
                )

            return {
                "player_id": player_id,
                "season": season,
                "games_played": len(stats),
                "stats": stats,
            }

        except Exception as e:
            return {"error": str(e)}, 500
