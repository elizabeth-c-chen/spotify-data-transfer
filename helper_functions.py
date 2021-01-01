import tekore as tk
import os
import math
import urllib.request


def setup_config(scope):
    """
    Configure setup for library-read step, return the spotify object
    which will interact with the Spotify API.
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


def get_subset_playlists(spotify, user_id, offsetcount, limit):
    """
    Get a subset of user_id's playlists specified by limit and offset.
    """
    offset = offsetcount*limit
    return spotify.playlists(user_id, limit=limit, offset=offset).items

def get_playlists(spotify, user_id):
    total_playlists = spotify.playlists(user_id).total
    print("{} has {} playlists in total".format(user_id, total_playlists))
    num_subsets = get_num_subsets(total_playlists, limit=50) # Max number of items per call is 50
    playlists = {}
    with spotify.chunked():
        for index in range(num_subsets):
            playlists[index] = get_subset_playlists(spotify, user_id, limit=50, offsetcount=index)
    return playlists


def playlist_info_to_lists(playlists):
    """
    Process playlist IDs and names from saved data to a list for use in the library-modify step.
    """
    playlist_ids = []
    playlist_names = []
    playlist_images = []
    playlist_descriptions = []
    for index in range(len(playlists)):
        simple_playlist_paging = playlists[index]
        for playlist in simple_playlist_paging:
            playlist_ids.append(playlist.id)
            playlist_names.append(playlist.name)
            playlist_images.append(playlist.images[0])
            playlist_descriptions.append(playlist.description)
    return playlist_ids, playlist_names, playlist_images, playlist_descriptions


def get_tracks_from_playlists(spotify, user_id, playlist_ids):
    """
    Get all tracks from each playlist for a given user.
    """
    data = {playlist_id: None for playlist_id in playlist_ids}
    for playlist_id in data.keys():
        with spotify.chunked():
            playlist_total_tracks = spotify.playlist_items(playlist_id).total
            num_subsets = get_num_subsets(playlist_total_tracks, limit=100)
            tracks = []
            for index in range(num_subsets):
                track_items = spotify.playlist_items(playlist_id, limit=100, offset=index*100).items
                tracks.append(track_items)
            data[playlist_id] = tracks
    return data


def flatten_playlist_get_track_uris(data):
    """
    Save track URIs in a single list (convert from list of lists).
    """
    data_new = {key: None for key in data.keys()}
    for playlist_id in data.keys():
        full_tracks = []
        for i in range(len(data[playlist_id])):
            tracks_i = data[playlist_id][i]
            for j in range(len(tracks_i)):
                track_uri = tracks_i[j].track.uri
                full_tracks.append(track_uri)
        data_new[playlist_id] = full_tracks
    print(data_new)
    return data_new


def find_playlists_with_cover_images(playlist_ids, playlist_names, playlist_images):
    """
    Look for playlists with custom images
    """
    images_to_add = {}
    for i in range(len(playlist_images)):
        img = playlist_images[i]
        playlist_name = playlist_names[i]
        playlist_id = playlist_ids[i]
        if img.height == None and img.width == None:
            images_to_add[playlist_id] = img.url
    return images_to_add

def save_images(images_to_add):
    """
    Save custom images to a local directory
    """
    if not os.path.exists('./cover_images'):
        os.mkdir('./cover_images')
    for playlist_id in images_to_add.keys():
        img_url = images_to_add[playlist_id]
        urllib.request.urlretrieve(img_url, './cover_images/' + playlist_id + '.jpeg')


def recreate_playlists(spotify, user_id, playlist_ids, tracks_flattened, playlist_names, playlist_descriptions):
    """
    Create a new playlists from given data.
    """
    for i in range(len(playlist_ids)):
        old_playlist_id = playlist_ids[i]
        name = playlist_names[i]
        description = playlist_descriptions[i]
        tracks_data = tracks_flattened[old_playlist_id]
        print("Creating new playlist named       '{}'".format(name))
        new_playlist = spotify.playlist_create(user_id, name=name, public=False, description=description)
        spotify.playlist_add(new_playlist.id, tracks_data)