# spotify-podcast-rss

Produces a simple RSS feed for podcasts on Spotify. Unfortunately not with links to mp3 files or such, since Spotify doesn't provide those. But still.

## Configuration

First, make sure you have a [Spotify app](https://developer.spotify.com/dashboard/applications).

Then, make an INI file with these contents:

```ini
[spotify]
client_id = (your client ID)
client_secret = (your client secret)
market = (your two-letter country code)
```

Default filename is `config.ini` in current directory. For any other filename, point to it via environment variable `SPR_CONFIG` or use `--config` parameter (see below).

## Usage

### Command line

When installed via `setup.py` or PIP, the command `spr` will point to `spr/cli.py`. This takes a Spotify show ID as parameter and outputs RSS to stdout.

Command line syntax:

```shell
spr [-c/--config (path to config file)] SPOTIFY_SHOW_ID
```

### WSGI

`spr.wsgi` contains a very simple WSGI application. It expects a URL ending with a Spotify show ID and outputs an RSS feed for that podcast, or a 404 response if the podcast was not found.
