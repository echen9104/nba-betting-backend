from flask_restx import fields, Namespace

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
        "three_pointers_attempted": fields.Integer(description="Three pointers attempted"),
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