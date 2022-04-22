import functools
import warnings
from datetime import timezone

import spotipy
from dateutil.parser import parse as datetime_parse
from feedgen.feed import FeedGenerator
from spotipy.oauth2 import SpotifyClientCredentials


def ignore_spotify_errors(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except spotipy.SpotifyException:
            return None
    return wrapper


class SPR:
    def __init__(self, client_id, client_secret, market=None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.market = market

        self.spotipy = spotipy.Spotify(
            auth_manager=SpotifyClientCredentials(client_id=client_id, client_secret=client_secret))

    @ignore_spotify_errors
    def get_episodes_by_show_id(self, show_id):
        eps = []
        offset = 0
        while True:
            ret = self.spotipy.show_episodes(show_id, limit=50, market=self.market, offset=offset)
            eps.extend([ep for ep in ret["items"] if ep["is_playable"]])
            if ret["next"] is None:
                break
            else:
                offset += 50
        return sorted(eps, key=lambda v: v.get("release_date", ""), reverse=True)

    @ignore_spotify_errors
    def get_show_by_show_id(self, show_id):
        return self.spotipy.show(show_id, market=self.market)

    def get_rss_by_show_id(self, show_id):
        show = self.get_show_by_show_id(show_id)
        if show is None:
            warnings.warn("get_show_by_show_id({}) returned None".format(show_id))
            return None
        eps = self.get_episodes_by_show_id(show_id)
        if eps is None:
            warnings.warn("get_episodes_by_show_id({}) returned None".format(show_id))

        fg = FeedGenerator()
        fg.load_extension("podcast")
        fg.id(show_id)
        fg.title(show["name"])
        if "href" in show:
            fg.link(href=show["href"], rel="via")
        if "images" in show and show["images"]:
            fg.logo(show["images"][0]["url"])
        if "languages" in show and show["languages"]:
            fg.language(show["languages"][0])
        fg.description(show.get("description", None))

        for ep in eps:
            if not ep["external_urls"]:
                continue
            url = None
            for key, value in ep["external_urls"].items():
                if key == "spotify":
                    url = value
                    break
            fe = fg.add_entry(order="append")
            fe.title(ep["name"])
            fe.id(ep["id"])
            fe.description(ep["description"])
            if len(ep["languages"]) == 1:
                fe.link(href=url, hreflang=ep["languages"][0])
            else:
                fe.link(href=url)
            if ep["explicit"]:
                fe.podcast.itunes_explicit("yes")
            if ep["images"]:
                # Spotify says the largest image will be first
                # We do a very ugly hack here because feedgen insists that the
                # string ends with '.jpg' or '.png'
                fe.podcast.itunes_image(ep["images"][0]["url"] + "#.jpg")
            try:
                published = datetime_parse(ep["release_date"])
                if published.tzinfo is None:
                    published = published.astimezone(timezone.utc)
                fe.published(published)
            except Exception:
                pass
            fe.podcast.itunes_duration(int(ep["duration_ms"] / 1000))
        return fg.rss_str(pretty=True)
