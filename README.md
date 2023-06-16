    # Brawl Stars Club League Data Tracker

    This Python program fetches data from the Brawl Stars API and organizes it into an Excel document. The program runs every other week during Club League weeks and updates player stats every 10 minutes. 

    ## Features

    - Fetches the latest player statistics from the Brawl Stars API
    - Only counts battles that occurred after the last time the program was run
    - Tracks player participation in the Club League on a weekly basis
    - Writes statistics to an Excel file that is synced to Google Drive

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

    Before you run the script, you will need to replace `your_key` and `your_club_tag` with your own API key and club tag. Your API key can be generated from the Brawl Stars API portal (https://developer.brawlstars.com/#/login). The club tag can be found in the Brawl Stars app under your club's profile.

    Here's how to set up the `auth_key` and `club_tag` variables:

    ```
    auth_key = "your_key"
    club_tag = "your_club_tag"

    headers = {
        "Accept": "application/json",
        "Authorization": "Bearer " + auth_key,
    }

    url_club = f"https://api.brawlstars.com/v1/clubs/{club_tag.replace('#', '%23')}/members"
    ```

    ## Usage

    It's recommended to run this script on a server or, if you're on Windows, use Task Scheduler to run the program every 10 minutes during Club League weeks. To automate the script execution, you can create a Basic Task in Task Scheduler and set the trigger to Daily, then set the "Repeat task every" option to 10 minutes for a duration of 24 hours. You can adjust the timings according to your needs.

    To avoid rate limiting from the API, the program waits for 3 seconds after each API request. The API allows for 100 requests per minute.

    Sync your Excel document with Google Drive to share the document with others. 

    ## Notes

    - The script creates `last_battle_time.txt` and `last_increment_week.txt` to avoid counting duplicate battles and weeks. 
    - Make sure to replace `%232R0Q2VV0C` with `%23your_club_tag`.
    - The program may take 35-60s to run due to the 3-second delay between API requests. This is to ensure the program stays within the API's rate limits.
    - The `time.sleep(3)` line in the script can be adjusted or removed if the delay is not necessary.
