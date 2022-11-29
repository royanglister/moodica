import os
import random
import spotipy  # A relatively lightweight library for integrating with Spotify's Web API for developers.
from spotipy.oauth2 import SpotifyOAuth
from datetime import datetime


# Setting the required environment variables.
os.environ["SPOTIPY_CLIENT_ID"] = 'f92617c590d148a7a3cd7de95e7147aa'
os.environ["SPOTIPY_CLIENT_SECRET"] = '2fdc699cf8394a93897b1a9c569ad1f4'
os.environ["SPOTIPY_REDIRECT_URI"] = "http://localhost:8080"

spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(scope="user-library-read,playlist-modify-private,playlist-read-private",
                                                    show_dialog=True, requests_session=True, state='IL'))  # Connecting to spotify.

# Key playlists for recommendations.
POPULAR_GLOBAL_PLAYLIST_URL = "https://open.spotify.com/playlist/37i9dQZEVXbNG2KDcFcKOF?si=1333723a6eff4b7f"  # Most popular songs globally.
POPULAR_LOCAL_PLAYLIST_URL = "https://open.spotify.com/playlist/37i9dQZF1DWSYF6geMtQMW"  # Most popular songs locally.

MIN_MOOD_PARAM = 0.0001
MAX_MOOD_PARAM = 0.99
MOOD_PARAMS_DICT = {"angry":        {'min_acousticness': MIN_MOOD_PARAM, 'max_acousticness': 0.1, 'min_danceability': 0.1,
                                     'max_danceability': 0.5, 'min_energy': 0.75, 'max_energy': MAX_MOOD_PARAM},
                    "fearful":      {'min_acousticness': MIN_MOOD_PARAM, 'max_acousticness': 0.5, 'min_danceability': MIN_MOOD_PARAM,
                                     'max_danceability': 0.5, 'min_energy': MIN_MOOD_PARAM, 'max_energy': MAX_MOOD_PARAM},
                    "happy":        {'min_acousticness': MIN_MOOD_PARAM, 'max_acousticness': 0.1, 'min_danceability': 0.5,
                                     'max_danceability': MAX_MOOD_PARAM, 'min_energy': 0.7, 'max_energy': MAX_MOOD_PARAM},
                    "neutral":      {'min_acousticness': MIN_MOOD_PARAM, 'max_acousticness': MAX_MOOD_PARAM, 'min_danceability': MIN_MOOD_PARAM,
                                     'max_danceability': MAX_MOOD_PARAM, 'min_energy': MIN_MOOD_PARAM, 'max_energy': MAX_MOOD_PARAM},
                    "sad":          {'min_acousticness': 0.125, 'max_acousticness': 0.5, 'min_danceability': 0.1,
                                     'max_danceability': 0.6, 'min_energy': 0.1, 'max_energy': 0.6},
                    "surprised":    {'min_acousticness': 0.075, 'max_acousticness': 0.2, 'min_danceability': 0.4,
                                     'max_danceability': MAX_MOOD_PARAM, 'min_energy': 0.3, 'max_energy': MAX_MOOD_PARAM}}

SEED_GENRES_LIST = ['acoustic', 'afrobeat', 'alt-rock', 'alternative', 'ambient', 'blues', 'chill', 'country', 'dance',
                    'deep-house', 'disco', 'dubstep', 'edm', 'electro' 'electronic', 'emo', 'folk', 'funk', 'guitar',
                    'happy', 'hard-rock', 'hip-hop', 'house', 'indie', 'indie-pop', 'latin', 'new-release', 'party',
                    'piano', 'pop', 'pop-film', 'progressive-house', 'punk', 'punk-rock', 'r-n-b', 'raggae',
                    'raggaeton', 'road-trip', 'rock', 'rock-n-roll', 'romance', 'sad', 'singer-songwriter',
                    'songwriter', 'soul', 'soundtracks', 'study', 'summer', 'synth-pop', 'techno', 'trance',
                    'trip-hop', 'work-out', 'world-music']  # Filtered from the total collection of spotify's genres.

MAX_CREATED_PLAYLISTS_NUM = 10

seed_tracks_ids_list = []
seed_artists_ids_list = []
recommended_tracks_uris_list = []
randomized_seed_genres_list = []

mood = ''


def prepare_seed_artists():
    """
    This function extracts a list of the playlists' artists.
    """
    global seed_artists_ids_list

    # Extracting playlists URIs.
    global_playlist_uri = POPULAR_GLOBAL_PLAYLIST_URL.split("/")[-1].split("?")[0]
    local_playlist_uri = POPULAR_LOCAL_PLAYLIST_URL.split("/")[-1].split("?")[0]

    # Adding the spotify id of every artist that appears in the playlists into a list.
    for x in spotify.playlist_items(global_playlist_uri)["items"]:
        seed_artists_ids_list.append(x["track"]["artists"][0]["id"])
    for x in spotify.playlist_items(local_playlist_uri)["items"]:
        seed_artists_ids_list.append(x["track"]["artists"][0]["id"])

    seed_artists_ids_list = list(dict.fromkeys(seed_artists_ids_list))  # Removing duplicates if there are any.
    random.shuffle(seed_artists_ids_list)  # Shuffling the seed artists list.


def prepare_seed_tracks():
    """
    This function extracts a list of the playlists' track IDs.
    """
    global seed_tracks_ids_list

    # Extracting playlists URIs.
    global_playlist_uri = POPULAR_GLOBAL_PLAYLIST_URL.split("/")[-1].split("?")[0]
    local_playlist_uri = POPULAR_LOCAL_PLAYLIST_URL.split("/")[-1].split("?")[0]

    # Extracting playlists' tracks IDs into a list.
    global_track_ids = [x["track"]["id"] for x in spotify.playlist_items(global_playlist_uri)["items"]]
    local_track_ids = [x["track"]["id"] for x in spotify.playlist_items(local_playlist_uri)["items"]]

    # Adding every track's ID that appears in the playlists into a list.
    for element in global_track_ids:
        seed_tracks_ids_list.append(element)
    for element in local_track_ids:
        seed_tracks_ids_list.append(element)

    seed_tracks_ids_list = list(dict.fromkeys(seed_tracks_ids_list))  # Removing duplicates if there are any.
    random.shuffle(seed_tracks_ids_list)  # Shuffling the seed tracks list.


def prepare_seed_genres():
    """
    This function extracts a shuffled list of the Spotify's genres.
    """
    global randomized_seed_genres_list

    randomized_seed_genres_list = SEED_GENRES_LIST
    random.shuffle(randomized_seed_genres_list)  # Shuffling the seed genres list.


def get_recommendations():
    """
    This function sends the collected data to Spotify's recommendation function and
    receives a serialized list that consists of recommended songs that are likely to
    match the user's mood.
    :return: A list that contains up to 10 songs and their details.
    :rtype: list
    """
    global mood
    global seed_artists_ids_list
    global randomized_seed_genres_list
    global seed_tracks_ids_list

    # A do-while loop that randomizes the number of recommendation seeds, so they sum up to a total of 5.
    while True:
        # Randomizing the numbers.
        seed_artists_num = random.randint(1, 4)
        seed_genres_num = random.randint(1, (5 - seed_artists_num))
        seed_tracks_num = 5 - (seed_artists_num + seed_genres_num)

        seed_numbers_list = [seed_artists_num, seed_genres_num, seed_tracks_num]
        if (seed_artists_num and seed_genres_num and seed_tracks_num) and (sum(seed_numbers_list) == 5):
            break

    recommendations = spotify.recommendations(seed_artists=seed_artists_ids_list[:seed_artists_num],
                                              seed_genres=randomized_seed_genres_list[:seed_genres_num],
                                              seed_tracks=seed_tracks_ids_list[:seed_tracks_num],
                                              limit=10, country='IL', min_popularity=40,
                                              min_acousticness=MOOD_PARAMS_DICT[mood]['min_acousticness'],
                                              max_acousticness=MOOD_PARAMS_DICT[mood]['max_acousticness'],
                                              min_danceability=MOOD_PARAMS_DICT[mood]['min_danceability'],
                                              max_danceability=MOOD_PARAMS_DICT[mood]['max_danceability'],
                                              min_energy=MOOD_PARAMS_DICT[mood]['min_energy'],
                                              max_energy=MOOD_PARAMS_DICT[mood]['max_energy'])
    return recommendations


def display_results(recommendations):
    """
    This function shows the playlist's contents in the terminal.
    :param recommendations:
    :return:
    """
    global mood
    global recommended_tracks_uris_list

    tracklist_info = []
    track_num = 1

    print("Mood detected: " + mood.capitalize() + '\n')
    for track in recommendations['tracks']:
        track_info = []

        print(str(track_num) + '\n' + "---")
        print('track name:     ' + str(track['name']))
        print('artist:         ' + str(track['artists'][0]['name']))
        print('audio preview:  ' + str(track['preview_url']))
        print('cover art:      ' + str(track['album']['images'][0]['url']))
        # print('popularity:     ' + str(track['popularity']))
        # print('audio features: ' + str(spotify.audio_features(track['uri'])[0].items())[12:-2])
        print("_______________________________________")
        print()
        recommended_tracks_uris_list.append(track['uri'])  # Adding the tracks' URIs to a list of tracks that will form the playlist's content.

        # Creating the songs list for the client's answer.
        track_info.append(str(track['name']))
        track_info.append(str(track['artists'][0]['name']))
        track_info.append(str(track['album']['images'][0]['url']))
        track_info.append(str(track['preview_url']))

        tracklist_info.append(track_info)
        track_num += 1

    return tracklist_info


def create_new_playlist():
    """
    This functions creates a new Spotify playlist that consists of the recommended songs.
    :return: The new playlist's URL.
    :rtype: str
    """
    global mood
    global recommended_tracks_uris_list

    # Creating a playlist name format.
    now = datetime.now()
    current_date_time = str(now.strftime("%d/%m/%Y, %H:%M:%S"))
    created_playlist_name = mood.capitalize() + " Playlist (" + current_date_time + ")"

    created_playlist = spotify.user_playlist_create(user=spotify.me()['id'], name=created_playlist_name,
                                                    public=False, collaborative=False)  # Creating an empty playlist.
    spotify.playlist_add_items(playlist_id=created_playlist['id'], items=recommended_tracks_uris_list)  # Adding the recommended tracks to the empty playlist.

    # Displaying the playlist's URL.
    created_playlist_url = spotify.user_playlists(user=spotify.me()['id'], limit=1)['items'][0]['external_urls']['spotify']  # Getting the URL of the latest playlist created.
    print("\n\n" + "View the full playlist version: ")
    print(created_playlist_url)

    return created_playlist_url


def maintain_history():
    """
    This function maintains a playlist history so only the newest 10 playlists are being
    displayed in the account at any given moment.
    """
    total_spotify_playlists_ids_list = []
    playlist_num = 0

    # Always keeping the newest 10 playlists (maintaining playlist history).
    total_spotify_playlists = spotify.user_playlists(user=spotify.me()['id'], limit=50)  # Getting all playlists of user.
    for playlist in total_spotify_playlists['items']:  # Counting the playlists by making a list of playlist IDs.
        total_spotify_playlists_ids_list.append(total_spotify_playlists['items'][playlist_num]['id'])
        playlist_num += 1

    if len(total_spotify_playlists_ids_list) > MAX_CREATED_PLAYLISTS_NUM:  # Removing the oldest playlist if there are more than 10 playlists.
        spotify.current_user_unfollow_playlist(total_spotify_playlists_ids_list[-1])


def activator(detected_mood):
    """
    This function activates the other functions in order to get the wanted results from Spotify.
    :param detected_mood:
    :return: The message to send the client - consists of the playlist's URL,
    the predicted mood, and the list of tracks that are in the playlist.
    :rtype: str
    """
    global mood

    mood = detected_mood
    prepare_seed_artists()
    prepare_seed_tracks()
    prepare_seed_genres()
    recommendations = get_recommendations()
    tracklist_info = display_results(recommendations)
    playlist_url = create_new_playlist()
    maintain_history()

    return str("'" + playlist_url + "'@'" + mood.capitalize() + "'@" + str(tracklist_info))
