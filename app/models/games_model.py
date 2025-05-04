from flask_restx import fields, Namespace

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