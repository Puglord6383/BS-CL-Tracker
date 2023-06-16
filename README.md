# Brawl Stars Club League Data Tracker

The Brawl Stars API does not directly include data for club league wins and losses, and therefore this data is not tracked on Brawl Stats, Brawlify, etc.
This is unfortunate because that could be a valuable tool for club leadership to track how many trophies each club member is earning over time, win/loss ratios, how many games are played with teams/randoms, etc.

This program is the solution to that. It pulls club data and for every player in the club, checks their battle log, and filters for battles that are 'teamRanked' which is power league, and have a trophy change, which means they are not standard power league matches and must be club league. From there, it sorts through based on:
-3 trophies = loss with randoms
-5 trophies = loss with club mate
-7 trophies = win with randoms
-9 trophies = win with club mate

Note: Untested, but non power league club league matches might not show up. If your club mates are intentionally throwing away trophies like that you should kick them or leave the club anyway.

All you need to do is edit the main.py file with your own API key and club tag, and set up Microsoft Office to sync your Excel file (was automatically set up on my system), and you have a spreadsheet of all your club mates CL data to manage your club with!

Note: Battle data is not uploaded to the API automatically. You will need to wait a while for it to start giving you helpful information. If you need to clear the spreadsheet, simply delete it while not deleting the last_battle_time.txt file.

Below is a full guide courtesy of chatGPT:

## Features

- Fetches the latest player statistics from the Brawl Stars API
- Only counts battles that occurred after the last time the program was run (untested)
- Tracks player participation in Club League on a weekly basis (untested)
- Writes statistics to an Excel file that can be synced to Microsoft Office to be shared

## Requirements

Python 3 and the following Python libraries are required:

- json
- requests
- pandas
- datetime
- time

You can install the required libraries using pip:

```
pip install requests pandas
```

## Configuration

Before you run the script, you must replace `your_key` and `your_club_tag` with your own API key and club tag. Your API key can be generated from the Brawl Stars API portal (https://developer.brawlstars.com/#/login). The club tag can be found in the Brawl Stars app under your club's profile.

Simply open the main.py file in a code editor and paste in your key and club tag:
```
auth_key = "your_key" # replace your_key with your api key
club_tag = "your_club_tag" # replace your_club_tag with your club tag (# instead of %23 is ok)

```
You can also update all instances of 'BS-CL-Tracker-Spreadsheet.xlsx' in the file to your name of choice.xlsx

## Usage

It's recommended to run this script on a server or, if you're on Windows, use Task Scheduler to run the program every once and a while. To automate the script execution, you can create a Basic Task in Task Scheduler and set the trigger to Daily, then set the "Repeat task every" option to 10 minutes (or whatever time you like) for a duration of 24 hours. You can adjust the timings according to your needs.

To avoid rate limiting from the API, the program waits for 1 second after each API request. The API allows for 100 requests per minute. You may edit this if you need it to run faster for some reason.

