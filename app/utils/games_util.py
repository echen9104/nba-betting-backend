def extract_game_data(data):
    game_data = []

    # Extract Game Header
    for game_header in data["GameHeader"]:
        game_info = {
            "game_date": game_header["GAME_DATE_EST"],
            "game_status": game_header["GAME_STATUS_TEXT"],
            "home_team": {
                "id": game_header["HOME_TEAM_ID"],
                "abbreviation": game_header["HOME_TV_BROADCASTER_ABBREVIATION"],
                "arena": game_header["ARENA_NAME"],
            },
            "visitor_team": {
                "id": game_header["VISITOR_TEAM_ID"],
                "abbreviation": game_header["AWAY_TV_BROADCASTER_ABBREVIATION"],
            },
            "live_period": game_header["LIVE_PERIOD"],
            "live_period_time_bcast": game_header["LIVE_PERIOD_TIME_BCAST"],
        }

        # Extract Line Score
        for line_score in data["LineScore"]:
            if line_score["GAME_ID"] == game_header["GAME_ID"]:
                game_info["line_score"] = {
                    "home_team_score": line_score["PTS"],
                    "home_team_field_goal_percentage": line_score["FG_PCT"],
                    "visitor_team_score": line_score["PTS"],
                    "visitor_team_field_goal_percentage": line_score["FG_PCT"],
                    "home_team_assists": line_score["AST"],
                    "visitor_team_assists": line_score["AST"],
                    "home_team_rebounds": line_score["REB"],
                    "visitor_team_rebounds": line_score["REB"],
                }

        # Extract Series Standings
        for series in data["SeriesStandings"]:
            if series["GAME_ID"] == game_header["GAME_ID"]:
                game_info["series_standings"] = {
                    "home_team_wins": series["HOME_TEAM_WINS"],
                    "home_team_losses": series["HOME_TEAM_LOSSES"],
                    "series_leader": series["SERIES_LEADER"],
                }

        # Extract Last Meeting
        for last_meeting in data["LastMeeting"]:
            if last_meeting["GAME_ID"] == game_header["GAME_ID"]:
                game_info["last_meeting"] = {
                    "last_game_home_team": last_meeting["LAST_GAME_HOME_TEAM_NAME"],
                    "last_game_visitor_team": last_meeting[
                        "LAST_GAME_VISITOR_TEAM_NAME"
                    ],
                    "last_game_home_team_points": last_meeting[
                        "LAST_GAME_HOME_TEAM_POINTS"
                    ],
                    "last_game_visitor_team_points": last_meeting[
                        "LAST_GAME_VISITOR_TEAM_POINTS"
                    ],
                }

        game_data.append(game_info)

    return game_data
