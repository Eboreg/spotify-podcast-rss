import os
from html import escape
from urllib.parse import parse_qs, urljoin

from spr import SPR, Config


def application(environ, start_response):
    # http://wsgi.tutorial.codepoint.net/application-interface
    # https://www.toptal.com/python/pythons-wsgi-server-application-interface

    config = Config.load()
    spr = SPR(**config.__dict__)

    if environ.get("REQUEST_METHOD").upper() == "POST":
        request_body = environ["wsgi.input"].read(-1).decode("utf-8")
        post = parse_qs(request_body)
        try:
            print(post, post.get("url_or_show_id", []))
            show_id = escape(post.get("url_or_show_id", [])[-1]).strip("/").split("/")[-1]
        except IndexError:
            show_id = ""
        start_response("303 See Other", [("Location", urljoin(environ.get("REQUEST_URI"), show_id))])
        return []

    show_id = environ.get("PATH_INFO").split("/")[-1]

    if not show_id:
        with open(os.path.join(os.path.dirname(__file__), "html/index.html")) as html:
            content = html.read().encode()
        content_type = "text/html; charset=utf-8"
        status = "200 OK"

    if show_id:  # not 'else', because show_id could have been reset above
        rss = spr.get_rss_by_show_id(show_id)
        if rss is None:
            content = "Show ID {} not found".format(show_id).encode()
            content_type = "text/plain; charset=utf-8"
            status = "404 Not Found"
        else:
            content = rss
            content_type = "application/rss+xml; charset=utf-8"
            status = "200 OK"

    # Debug stuff
    # content = "\n".join(["%s: %s" % (k, v) for k, v in sorted(environ.items())]).encode()
    # status = "200 OK"
    # content_type = "text/plain; charset=utf-8"

    response_headers = [
        ("Content-Type", content_type),
        ("Content-Length", str(len(content))),
    ]

    start_response(status, response_headers)

    if environ.get("REQUEST_METHOD").upper() == "HEAD":
        return []

    return [content]
