import tekore as tk
import math
import os
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


def get_subset_playlists(spotify, user_id, offsetcount, limit):
    """
    Get a subset of user_id's playlists specified by limit and offset.
    """
    offset = offsetcount*limit
    return spotify.playlists(user_id, limit=limit, offset=offset).items


def get_playlists(spotify, user_id, limit=50):
    total_playlists = spotify.playlists(user_id).total
    print("{} has {} playlists in total".format(user_id, total_playlists))
    num_subsets = get_num_subsets(total_playlists, limit=50) # Max number of items per call is 50
    playlists = {}
    with spotify.chunked():
        for index in range(num_subsets):
            playlists[index] = get_subset_playlists(spotify, user_id, limit=limit, offsetcount=index)
    return playlists


def playlist_info_to_lists(playlists):
    """
    Process playlist IDs and names from saved data to a list for use in the library-modify step.
    """
    playlist_ids = []
    playlist_names = []
    playlist_images = []
    for index in range(len(playlists)):
        simple_playlist_paging = playlists[index]
        for playlist in simple_playlist_paging:
            playlist_ids.append(playlist.id)
            playlist_names.append(playlist.name)
            playlist_images.append(playlist.images[0])
    return playlist_ids, playlist_names, playlist_images


def find_playlists_with_cover_images(playlist_ids, playlist_names, playlist_images):
    """
    Look for playlists with custom images
    """
    images_to_add = {}
    for i in range(len(playlist_images)):
        img = playlist_images[i]
        playlist_name = playlist_names[i]
        playlist_id = playlist_ids[i]
        if img.height is None and img.width is None:
            images_to_add[playlist_id] = (playlist_name, img.url)
    return images_to_add


def save_images(images_to_add):
    """
    Save custom images to a local directory
    """
    if not os.path.exists('./cover_images'):
        os.mkdir('./cover_images')
    for playlist_id in images_to_add.keys():
        playlist_name, img_url = images_to_add[playlist_id]
        urllib.request.urlretrieve(img_url, './cover_images/' + playlist_name + '.jpeg')


if __name__ == '__main__':
    spotify_src = setup_config(tk.scope.read)
    user_id_src = spotify_src.current_user().id
    print("Now retrieving playlists....")
    playlists = get_playlists(spotify_src, user_id_src, limit=5)
    playlist_ids, playlist_names, playlist_images = playlist_info_to_lists(playlists)
    img_2_add = find_playlists_with_cover_images(playlist_ids, playlist_names, playlist_images)
    save_images(img_2_add)
