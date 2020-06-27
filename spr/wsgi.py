from spr import SPR, Config


def application(environ, start_response):
    # http://wsgi.tutorial.codepoint.net/application-interface

    config = Config.load()
    spr = SPR(**config.__dict__)

    show_id = environ.get("PATH_INFO").split("/")[-1]
    rss = spr.get_rss_by_show_id(show_id)

    if rss is None:
        content = b"Not Found"
        content_type = "text/plain; charset=utf-8"
        status = "404 Not Found"
    else:
        content = rss
        content_type = "application/rss+xml; charset=utf-8"
        status = "200 OK"

    response_headers = [
        ("Content-Type", content_type),
        ("Content-Length", str(len(content))),
    ]

    start_response(status, response_headers)

    return [content]
