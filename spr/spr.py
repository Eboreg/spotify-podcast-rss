import spotipy
from spotipy.oauth2 import SpotifyClientCredentials


class SPR:
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret

        self.spotipy = spotipy.Spotify(
            auth_manager=SpotifyClientCredentials(client_id=client_id, client_secret=client_secret))
