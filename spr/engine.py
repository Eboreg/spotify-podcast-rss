import functools
from typing import cast
import warnings
from datetime import timezone

import spotipy
from dateutil.parser import parse as datetime_parse
from feedgen.feed import FeedGenerator
from feedgen.entry import FeedEntry
from feedgen.ext.podcast_entry import PodcastEntryExtension
from spotipy.oauth2 import SpotifyClientCredentials


def ignore_spotify_errors(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except spotipy.SpotifyException:
            return None
    return wrapper


class PodcastFeedEntry(FeedEntry):
    podcast: PodcastEntryExtension


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
            if ret:
                eps.extend([ep for ep in ret["items"] if ep["is_playable"]])
            if ret is None or ret["next"] is None:
                break
            offset += 50
        return sorted(eps, key=lambda v: v.get("release_date", ""), reverse=True)

    @ignore_spotify_errors
    def get_show_by_show_id(self, show_id):
        return self.spotipy.show(show_id, market=self.market)

    def get_rss_by_show_id(self, show_id):
        show = self.get_show_by_show_id(show_id)
        if show is None:
            warnings.warn(f"get_show_by_show_id({show_id}) returned None")
            return None
        eps = self.get_episodes_by_show_id(show_id)
        if eps is None:
            warnings.warn(f"get_episodes_by_show_id({show_id}) returned None")

        fg = FeedGenerator()
        fg.load_extension("podcast")
        fg.id(show_id)
        fg.title(show["name"])
        if "href" in show:
            fg.link(href=show["href"], rel="via")
        if "images" in show and show["images"]:
            fg.logo(logo=show["images"][0]["url"])
        if "languages" in show and show["languages"]:
            fg.language(show["languages"][0])
        fg.description(show.get("description", None))

        for ep in eps:
            # pylint: disable=no-member
            if not ep["external_urls"]:
                continue
            url = None
            for key, value in ep["external_urls"].items():
                if key == "spotify":
                    url = value
                    break
            fe = cast(PodcastFeedEntry, fg.add_entry(order="append"))
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
