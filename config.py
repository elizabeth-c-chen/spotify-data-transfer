import tekore as tk
import os
"""
TODO Change the three fields below to your Spotify Developer Client ID, 
Client Secret, and your specified Redirect URI (access via the green 
"Edit Settings" button).
TODO Run python3 config.py to create the credentials.ini file
"""

client_id = os.environ.get("CLIENT_ID") # TODO 
client_secret = os.environ.get("CLIENT_SECRET") # TODO 
redirect_uri = "http://localhost/" 

conf = (client_id, client_secret, redirect_uri)
tk.config_to_file('credentials.ini', conf)
