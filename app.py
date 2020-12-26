import tekore as tk
import os
import math

def setup_config(scope):
    """
    Configure setup for library-read step, return the spotify object
    which will retrieve the data.
    """
    conf = tk.config_from_file('credentials.ini')
    token = tk.prompt_for_user_token(*conf, scope=scope)
    spotify = tk.Spotify(token, chunked_on=True)
    return spotify

def get_num_subsets(total, limit):
    """
    Calculate how many subsets are needed given a max limit.
    """
    return int(math.ceil(total/limit))

def get_subset_tracks(spotify, offsetcount, limit):
    """
    Get saved tracks at location specified by offsetcount*limit.
    """
    offset = offsetcount*limit
    return spotify.saved_tracks(limit=limit, offset=offset).items

def get_library(spotify):
    """
    Retrieve library for user and return the data.
    """
    total_size = spotify.saved_tracks().total # Get total number of tracks in library.
    num_subsets = get_num_subsets(total_size, limit=50) # Max number of items per call is 50
    data = {}
    with spotify.chunked(): # Chunking to avoid API overuse
        for index in range(num_subsets):
            data[index] = get_subset_tracks(spotify, index, limit=50)
    return data

def track_ids_to_list(data):
    """
    Process track IDs from saved data to a list for use in the library-modify step.
    """
    track_ids = []
    for index in range(len(data)):
        saved_track_paging = data[index]
        for saved_item in saved_track_paging:
            track_ids.append(saved_item.track.id)
    return track_ids

def transfer(spotify, track_ids):
    """
    Given a spotify object and a list of track IDs, add all tracks to Library.
    """
    with spotify.chunked():
        spotify.saved_tracks_add(track_ids)

def run_transfer():
    answer = ""
    while answer != "exit":
        answer = input("The following program will transfer data between two Spotify accounts. Are you OK with that? [yes/no/exit]  ")
        if answer.lower() == "yes":
            break
        elif answer.lower() == "no" or answer.lower() == "exit":
            print("Now exiting the transfer process.")
            return
        else:
            continue
    # Step 1: Log in and authorize the application from source account
    print("""Step 1: First we require authorization from the source account.
             A new browser window will open now. Please give access to the app in order to proceed.""")
    spotify_src = setup_config(tk.scope.user_library_read)
    
    # Step 2: Retrieve data and put all track IDs in a single list 
    print("""Step 2: Retrieving all saved tracks from source account.""")
    data = get_library(spotify_src)
    track_ids = track_ids_to_list(data)
    
    # Step 3: Now logout of source account
    print("""Step 3: Data has been successfully retrieved. [MANDATORY] Please go to spotify.com and logout of source account entirely.""")
    confirmation = ""
    while confirmation != "exit":
        confirmation = input("Please confirm that you have logged out of the source account. [yes/exit]  ")
        if confirmation.lower() == "yes":
            break
        elif confirmation.lower() == "exit":
            print("Now exiting the transfer process.")
            return
        else: 
            continue
    # Step 4: Authorize destination account.
    print("""Step 4: Now you will authorize the app for the destination account. Please log in with your new account credentials.""")
    spotify_dest = setup_config(tk.scope.user_library_modify)

    # Step 5: Transfer the songs!
    print("Now transferring all songs...")
    transfer(spotify_dest, track_ids)
    print("Transfer has finished. Please check your destination account Library to view the added songs.")

if __name__ == "__main__":
    run_transfer()
