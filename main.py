auth_key = "your_key"  # replace your_key with your api key
club_tag = "your_club_tag"  # replace your_club_tag with your club tag (# instead of %23 is ok)

import time
import json
import requests
import pandas as pd
import datetime
import numpy as np

headers = {
    "Accept": "application/json",
    "Authorization": "Bearer " + auth_key,
}

# Replace '#' with '%23' in the club tag
club_tag = club_tag.replace('#', '%23')

# Insert the club tag into the URL
url_club = f"https://api.brawlstars.com/v1/clubs/{club_tag}/members"

response_club = requests.get(url_club, headers=headers)
data_club = response_club.json()

club_members = {member['tag'].replace('#', '%23'): member['name'] for member in data_club['items']}

try:
    df_existing = pd.read_excel('BS-CL-Tracker-Spreadsheet.xlsx', index_col=0)
    total_updates = df_existing.iloc[0]['Total Updates'] + 1 if 'Total Updates' in df_existing.columns and 'Last Update Time' in df_existing.columns else 1
    player_stats = df_existing.to_dict(orient='index')
except FileNotFoundError:
    total_updates = 1
    player_stats = {}

try:
    with open('last_battle_time.txt', 'r') as f:
        last_battle_time = datetime.datetime.strptime(f.read(), '%Y%m%dT%H%M%S.%fZ')
except FileNotFoundError:
    last_battle_time = datetime.datetime.min

try:
    with open('last_increment_week.txt', 'r') as f:
        last_increment_week = datetime.datetime.strptime(f.read(), '%Y%m%d')
except FileNotFoundError:
    last_increment_week = datetime.datetime.min

most_recent_battle_time = last_battle_time

# Initialize player stats for new players
for player_name in club_members.values():
    if player_name not in player_stats:
        player_stats[player_name] = {'Trophies': 0, 'Wins': 0, 'Losses': 0, 'Team': 0, 'Solo': 0, 'Team Wins': 0, 'Team Losses': 0, 'Solo Wins': 0, 'Solo Losses': 0, 'Weeks': 0}

for player_id, player_name in club_members.items():
    url_battlelog = f"https://api.brawlstars.com/v1/players/{player_id}/battlelog"
    response_battlelog = requests.get(url_battlelog, headers=headers)
    data_battlelog = response_battlelog.json()

    initial_trophies = player_stats[player_name]['Trophies'] if player_name in player_stats else 0

    for item in data_battlelog['items']:
        battle_time = datetime.datetime.strptime(item['battleTime'], '%Y%m%dT%H%M%S.%fZ')

        if battle_time > last_battle_time and 'battle' in item and 'type' in item['battle'] and item['battle']['type'] == 'teamRanked':
            trophy_change = item['battle'].get('trophyChange')

            if trophy_change == 3:
                player_stats[player_name]['Losses'] += 1
                player_stats[player_name]['Solo Losses'] += 1
            elif trophy_change == 5:
                player_stats[player_name]['Losses'] += 1
                player_stats[player_name]['Team Losses'] += 1
            elif trophy_change == 7:
                player_stats[player_name]['Wins'] += 1
                player_stats[player_name]['Solo Wins'] += 1
            elif trophy_change == 9:
                player_stats[player_name]['Wins'] += 1
                player_stats[player_name]['Team Wins'] += 1

            player_stats[player_name]['Trophies'] += trophy_change if trophy_change is not None else 0
            player_stats[player_name]['Team'] += 1 if trophy_change in [5, 9] else 0
            player_stats[player_name]['Solo'] += 1 if trophy_change in [3, 7] else 0

            if battle_time > most_recent_battle_time:
                most_recent_battle_time = battle_time

# Save most recent battle time
with open('last_battle_time.txt', 'w') as f:
    f.write(most_recent_battle_time.strftime('%Y%m%dT%H%M%S.%fZ'))

# Increment week counter if necessary
if datetime.datetime.now().date() - last_increment_week.date() >= datetime.timedelta(days=7):
    for player_name in club_members.values():
        player_stats[player_name]['Weeks'] += 1
    last_increment_week = datetime.datetime.now()
    with open('last_increment_week.txt', 'w') as f:
        f.write(last_increment_week.strftime('%Y%m%d'))

# Save player stats
df = pd.DataFrame(player_stats).T
df['Win/Loss Ratio'] = np.divide(df['Wins'], df['Wins'] + df['Losses'], where=(df['Wins']+df['Losses'])!=0)
df['Team/Random Ratio'] = np.divide(df['Team'], df['Team'] + df['Solo'], where=(df['Team']+df['Solo'])!=0)
df = df.sort_values(by='Trophies', ascending=False)
last_update_time = datetime.datetime.now()
df.loc[df.index[0], 'Total Updates'] = total_updates
df.loc[df.index[0], 'Last Update Time'] = last_update_time.strftime('%Y-%m-%d %H:%M:%S')
df.to_excel('BS-CL-Tracker-Spreadsheet.xlsx')
