from datetime import datetime
from nba_api.stats.endpoints import ScoreboardV2
from app.utils.nba_api import extract_game_data

def get_today_games():
    today_str = datetime.now().strftime('%m/%d/%Y')
    scoreboard = ScoreboardV2(game_date=today_str)
    data = scoreboard.get_normalized_dict()
    
    extracted_data = extract_game_data(data)
    return {'date': today_str, 'games': extracted_data} 