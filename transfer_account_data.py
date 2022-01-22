import tekore as tk
from helper_functions import *


# Part 1: Retrieve all playlist data and library from source account
print("Please log in with the source account:")
spotify_src = setup_config()
user_id_src = spotify_src.current_user().id
print("Now retrieving library data....")
library = get_library(spotify_src)
print("Finished retrieving library data!")
lib_track_ids = track_ids_to_list(library)
print("Now retrieving playlists data....")
playlists = get_playlists(spotify_src, user_id_src)
print("Finished retrieving playlist info!")
print("Now retrieving all track data for each playlist...")
playlist_ids, playlist_names, playlist_images, playlist_descriptions = playlist_info_to_lists(playlists)
tracks_data = get_tracks_from_playlists(spotify_src, user_id_src, playlist_ids)
print("Finished retrieving full playlist data!")
#tracks_flattened = flatten_playlist_get_track_uris(tracks_data)

# OPTIONAL: save cover images to local directory
#img_2_add = find_playlists_with_cover_images(playlist_ids, playlist_names, playlist_images)
#save_images(img_2_add)

# Part 2: Then log into destination account and write data to new account
print("Please log in with the destination account:")
spotify_dest = setup_config()
user_id_dest = spotify_dest.current_user().id
print("Now recreating all playlists...")
recreate_playlists(spotify_dest, user_id_dest, playlist_ids, tracks_data, playlist_names, playlist_descriptions) #, playlist_images)
print("Finished recreating playlists!")
print("Now copying saved songs...")
transfer_library(spotify_dest, lib_track_ids) 
print("Finished copying saved songs!")
print("Transfer is complete!")   
