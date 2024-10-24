import csv
import requests
from datetime import datetime

# Timestamp to date
def convert_timestamp_to_date(timestamp):
    return datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

# Civ Mapping (might change with new civs DLC)
civ_list = {
    1: "Aztecs", 2: "Bengalis", 3: "Berbers", 4: "Bohemians", 5: "Britons",
    6: "Bulgarians", 7: "Burgundians", 8: "Burmese", 9: "Byzantines", 10: "Celts",
    11: "Chinese", 12: "Cumans", 13: "Dravidians", 14: "Ethiopians", 15: "Franks",
    17: "Goths", 18: "Gurjaras", 19: "Huns", 20: "Incas", 21: "Indians",
    22: "Italians", 23: "Japanese", 24: "Khmer", 25: "Koreans", 26: "Lithuanians",
    27: "Magyars", 28: "Malay", 29: "Malians", 30: "Mayans", 31: "Mongols",
    32: "Persians", 33: "Poles", 34: "Portuguese", 36: "Saracens", 37: "Sicilians",
    38: "Slavs", 39: "Spanish", 40: "Tatars", 41: "Teutons", 42: "Turks",
    43: "Vietnamese", 44: "Vikings", 35: "Romans", 0: "Armenians", 16: "Georgians"
}

# Set platform based on user choice
platform = 'xboxlive'

# Prompt user for the player's ID
playerid = 'F7577FE856E4AEDA15094BF4CEA3610BA6403A5D'

# API
URL = 'https://aoe-api.worldsedgelink.com/community/leaderboard/getRecentMatchHistory?title=age2&profile_names=[%22/xboxlive/F7577FE856E4AEDA15094BF4CEA3610BA6403A5D%22]'
TIMEOUT = 10

today = datetime.now()


# Get data
try:
    response = requests.get(URL, timeout=10)
    player_data = response.json()

    # Check if 'matchHistoryStats' key is present
    if 'matchHistoryStats' in player_data:
        # Process the matches
        matches = player_data['matchHistoryStats']

        profiles = player_data['profiles']
        profile_id_to_alias = {profile['profile_id']: profile['alias'] for profile in profiles}

        # Convert timestamp to date
        for match in matches:
            match['startgametime'] = convert_timestamp_to_date(match['startgametime'])

        # Sort matches by date
        matches.sort(key=lambda x: x['startgametime'], reverse=True)

        # Create or append to existing CSV file
        csv_filename = f"match_history_{today}.csv"
        with open(csv_filename, mode='a', newline='') as csv_file:
            fieldnames = ['Date', 'Map', 'Team', 'Result', 'Alias', 'Elo', 'Civilization']
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

            # If the file is empty, write header
            if csv_file.tell() == 0:
                writer.writeheader()

            # Extract player information for each match
            for match in matches:
                player_info = []
                for member in match['matchhistorymember']:
                    profile_id = member['profile_id']
                    alias = profile_id_to_alias.get(profile_id, f"Unknown Alias for {profile_id}")
                    player_info.append({
                        'alias': alias,
                        'name': member['profile_id'],
                        'civ': member['civilization_id'],
                        'elo': member['oldrating'],
                        'result': member['outcome'],
                        'team': member['teamid']
                    })

                # Group player information by team
                grouped_by_team = {}
                for player in player_info:
                    team_id = player['team']
                    if team_id not in grouped_by_team:
                        grouped_by_team[team_id] = []
                    grouped_by_team[team_id].append(player)

                # Determine match result for each team
                for team_id, team_players in grouped_by_team.items():
                    team_result = "Won" if team_players[0]['result'] == 1 else "Lost"

                    # Write match information to CSV file
                    for player in team_players:
                        writer.writerow({
                            'Date': match['startgametime'],
                            'Map': match['mapname'],
                            'Team': f"Team {team_id+1}",
                            'Result': team_result,
                            'Alias': player['alias'],
                            'Elo': player['elo'],
                            'Civilization': civ_list.get(player['civ'], "Unknown")
                        })

            print(f"Match history saved to {csv_filename}")

    else:
        print(f"No matches found for {platform.capitalize()} ID: {playerid}")

except requests.RequestException as e:
    print(f"Request failed: {e}")
except KeyError:
    print(f"Invalid response format. No 'matchHistoryStats' key found. No matches for {platform.capitalize()} ID: {playerid}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
