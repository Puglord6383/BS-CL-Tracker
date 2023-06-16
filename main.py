auth_key = "your_key" # replace your_key wih your api key
club_tag = "your_club_tag" # replace your_club_tag with your club tag (# instead of %23 is ok)

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

# Fetch club members
#print('Fetching club members...')
#time.sleep(1)
response_club = requests.get(url_club, headers=headers)
data_club = response_club.json()

# Handle the response for club members
#if response_club.status_code == 200:
    #print(f'Successfully fetched club members: {len(data_club["items"])} members found.')
#else:
    #print(f'Failed to fetch club members: {response_club.status_code} - {data_club["message"]}')

# Generate club members dictionary
club_members = {member['tag'].replace('#', '%23'): member['name'] for member in data_club['items']}

# Try to load existing player stats, last processed battleTime, and the week counter from files
try:
    df_existing = pd.read_excel('BS-CL-Tracker-Spreadsheet.xlsx', index_col=0)
    if 'Total Updates' in df_existing.columns and 'Last Update Time' in df_existing.columns:
        total_updates = df_existing.iloc[0]['Total Updates'] + 1
    else:
        total_updates = 1
except FileNotFoundError:
    total_updates = 1

try:
    player_stats = pd.read_excel('BS-CL-Tracker-Spreadsheet.xlsx', index_col=0).to_dict(orient='index')
except FileNotFoundError:
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

# Initialize the weeks for new players and set the most recent battle time
most_recent_battle_time = last_battle_time

for player_name in club_members.values():
    if player_name not in player_stats:
        player_stats[player_name] = {'Trophies': 0, 'Wins': 0, 'Losses': 0, 'Team': 0, 'Solo': 0, 'Team Wins': 0, 'Team Losses': 0, 'Solo Wins': 0, 'Solo Losses': 0, 'Weeks': 0}

for player_id, player_name in club_members.items():
    url_battlelog = f"https://api.brawlstars.com/v1/players/{player_id}/battlelog"   # player battle logs
    #time.sleep(1)
    response_battlelog = requests.get(url_battlelog, headers=headers)
    
    #if response_battlelog.status_code == 200:
        #print(f'Successfully fetched data for player {player_name}')
    #else:
        #data_battlelog = response_battlelog.json()
        #print(f'Failed to fetch data for player {player_name}: {response_battlelog.status_code} - {data_battlelog["message"]}')
        #continue

    data_battlelog = response_battlelog.json()
    
    initial_trophies = player_stats[player_name]['Trophies'] if player_name in player_stats else 0

    if player_name not in player_stats:
        player_stats[player_name] = {'Trophies': 0, 'Wins': 0, 'Losses': 0, 'Team': 0, 'Solo': 0, 'Team Wins': 0, 'Team Losses': 0, 'Solo Wins': 0, 'Solo Losses': 0}

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
    trophies_added = player_stats[player_name]['Trophies'] - initial_trophies
    #print(f"{player_name} added {trophies_added} trophies.")

# Save player stats and last processed battleTime to files
df = pd.DataFrame(player_stats).T

# Calculate ratios
df['Win/Loss Ratio'] = np.divide(df['Wins'], df['Wins'] + df['Losses'], where=(df['Wins']+df['Losses'])!=0)
df['Team/Random Ratio'] = np.divide(df['Team'], df['Team'] + df['Solo'], where=(df['Team']+df['Solo'])!=0)

# Sort the DataFrame by 'Trophies' column in descending order
df = df.sort_values(by='Trophies', ascending=False)

# Add total updates and last update time
last_update_time = datetime.datetime.now()
df.loc[df.index[0], 'Total Updates'] = total_updates
df.loc[df.index[0], 'Last Update Time'] = last_update_time.strftime('%Y-%m-%d %H:%M:%S')

# Update the last_battle_time.txt file only once, after processing all battle logs
with open('last_battle_time.txt', 'w') as f:
    f.write(most_recent_battle_time.strftime('%Y%m%dT%H%M%S.%fZ'))

# At the end of processing the battle log for each player
if datetime.datetime.now().date() - last_increment_week.date() >= datetime.timedelta(days=7):
    for player_name in club_members.values():
        player_stats[player_name]['Weeks'] += 1
    last_increment_week = datetime.datetime.now()
    with open('last_increment_week.txt', 'w') as f:
        f.write(last_increment_week.strftime('%Y%m%d'))

df.to_excel('BS-CL-Tracker-Spreadsheet.xlsx')
