from flask_restx import fields, Namespace

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

player_stats_model = api.model(
    "PlayerStats",
    {
        "game_id": fields.String(description="Unique identifier for the game"),
        "game_date": fields.String(description="Date of the game"),
        "matchup": fields.String(description="Teams playing in the game"),
        "result": fields.String(description="Game result (W/L)"),
        "minutes": fields.String(description="Minutes played"),
        "points": fields.Integer(description="Points scored"),
        "rebounds": fields.Integer(description="Total rebounds"),
        "assists": fields.Integer(description="Assists"),
        "steals": fields.Integer(description="Steals"),
        "blocks": fields.Integer(description="Blocks"),
        "field_goals_made": fields.Integer(description="Field goals made"),
        "field_goals_attempted": fields.Integer(description="Field goals attempted"),
        "three_pointers_made": fields.Integer(description="Three pointers made"),
        "three_pointers_attempted": fields.Integer(description="Three pointers attempted"),
        "free_throws_made": fields.Integer(description="Free throws made"),
        "free_throws_attempted": fields.Integer(description="Free throws attempted"),
        "turnovers": fields.Integer(description="Turnovers"),
        "plus_minus": fields.Integer(description="Plus/minus rating"),
    },
)

player_stats_response = api.model(
    "PlayerStatsResponse",
    {
        "player_id": fields.Integer(description="Player ID"),
        "season": fields.String(description="NBA season"),
        "games_played": fields.Integer(description="Number of games played"),
        "stats": fields.List(fields.Nested(player_stats_model)),
    },
) 