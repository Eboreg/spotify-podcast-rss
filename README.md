# spotify-podcast-rss

Produces a simple RSS feed for podcasts on Spotify. Unfortunately not with links to mp3 files or such, since Spotify doesn't provide those. But still.

## Installation

```shell
python -m venv .venv
source .venv/bin/activate
pip install .
# To install dev and www packages: pip install .[dev,www]
```

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

`spr.wsgi` contains a very simple WSGI application. Given a URL ending with a Spotify show ID, it outputs an RSS feed for that podcast, or a 404 response if the podcast was not found. Without show ID, it gives you a wonderfully primitive HTML form, which accepts a show ID or a full Spotify show URL.

In order to use this, the package needs to be installed with the `www` extra (e.g. `pip install .[www]`).
