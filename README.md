
# Spotify Data Transfer Tool
I created this tool out of a personal wish to copy all my Spotify data to a new account. It allows for copying all playlists owned by a user and copying all saved songs in their library.

### Usage
Update the `config.py` file with your Spotify Developer credentials and set a redirect URI (http://localhost/ is fine, it will just lead to a "cannot find server" page -- just copy and paste the URL from the address bar when running the `app.py` file). 
Then run `python3 config.py` to generate the credentials file. Finally, run `python3 app.py` and login to Spotify when prompted. See file and helper functions for more information.

### Disclaimer
I created this for personal use so I can't guarantee it will work for everything you want it to or that it will work in all cases!
