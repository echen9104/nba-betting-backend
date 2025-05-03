from flask import Blueprint, jsonify, request
from nba_api.stats.endpoints import PlayerGameLogs, CommonPlayerInfo, CommonAllPlayers
from nba_api.stats.library.parameters import SeasonAll

players_bp = Blueprint('players', __name__)

@players_bp.route('/players/search', methods=['GET'])
def search_players():
    try:
        name = request.args.get('name')
        if not name:
            return jsonify({'error': 'Name parameter is required'}), 400
            
        # Get all players and filter by name
        all_players = CommonAllPlayers()
        data = all_players.get_normalized_dict()
        
        # Filter players by name
        matching_players = [
            player for player in data['CommonAllPlayers']
            if name.lower() in f"{player['DISPLAY_FIRST_LAST']}".lower()
        ]
        
        if not matching_players:
            return jsonify({'error': 'No players found'}), 404
            
        players = []
        for player in matching_players:
            players.append({
                'player_id': player['PERSON_ID'],
                'name': player['DISPLAY_FIRST_LAST'],
                'team': player['TEAM_CITY'] + ' ' + player['TEAM_NAME'],
                'position': player.get('POSITION', 'N/A'),
                'jersey_number': player.get('JERSEY', 'N/A')
            })
            
        return jsonify({
            'count': len(players),
            'players': players
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@players_bp.route('/players/<int:player_id>', methods=['GET'])
def get_player_info(player_id):
    try:
        player_info = CommonPlayerInfo(player_id=player_id)
        data = player_info.get_normalized_dict()
        
        if not data['CommonPlayerInfo']:
            return jsonify({'error': 'Player not found'}), 404
            
        player = data['CommonPlayerInfo'][0]
        return jsonify({
            'player_id': player_id,
            'name': f"{player['FIRST_NAME']} {player['LAST_NAME']}",
            'team': player['TEAM_NAME'],
            'position': player['POSITION'],
            'height': player['HEIGHT'],
            'weight': player['WEIGHT'],
            'birth_date': player['BIRTH_DATE'],
            'years_pro': player['SEASON_EXP']
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@players_bp.route('/players/<int:player_id>/stats', methods=['GET'])
def get_player_stats(player_id):
    try:
        # Get player's game logs for the current season
        player_logs = PlayerGameLogs(
            player_id_nullable=player_id,
            season_nullable=SeasonAll.current_season
        )
        
        # Get the data as a dictionary
        data = player_logs.get_normalized_dict()
        
        # Extract relevant stats
        stats = []
        for game in data['PlayerGameLogs']:
            game_stats = {
                'game_id': game['GAME_ID'],
                'game_date': game['GAME_DATE'],
                'matchup': game['MATCHUP'],
                'points': game['PTS'],
                'rebounds': game['REB'],
                'assists': game['AST'],
                'steals': game['STL'],
                'blocks': game['BLK'],
                'field_goal_percentage': game['FG_PCT'],
                'three_point_percentage': game['FG3_PCT'],
                'free_throw_percentage': game['FT_PCT'],
                'minutes_played': game['MIN']
            }
            stats.append(game_stats)
        
        return jsonify({
            'player_id': player_id,
            'games_played': len(stats),
            'stats': stats
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500 