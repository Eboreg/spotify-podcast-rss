from html import escape
from urllib.parse import parse_qs, urlparse
from wsgiref.types import StartResponse, WSGIEnvironment

from jinja2 import Environment, PackageLoader, select_autoescape

from spr import SPR, Config


jinja = Environment(
    loader=PackageLoader("spr", "html"),
    autoescape=select_autoescape(),
)


class ResponseData:
    def __init__(self, content: bytes = b"", content_type: str = "text/plain; charset=utf-8", status: str = "200 OK"):
        self.content = content
        self.content_type = content_type
        self.status = status


def get_show_context(environ: WSGIEnvironment, show_id: str) -> dict:
    config = Config.load()
    spr = SPR(**config.__dict__)

    try:
        show = spr.spotipy.show(show_id=show_id)
        scheme = environ.get("wsgi.url_scheme", "https")
        host = environ.get("HTTP_HOST", "")
        path = urlparse(environ.get("REQUEST_URI", "")).path.strip("/")

        return {
            "show": {
                "name": show["name"],
                "feed_url": f"{scheme}://{host}/{path}/{show_id}",
            },
        }
    except Exception as e:
        return {"error": f"Error when looking up podcast: {e}"}


def get_index(environ: WSGIEnvironment) -> ResponseData:
    context: dict = {}
    template = jinja.get_template("index.html")
    query = parse_qs(environ.get("QUERY_STRING", ""))
    qlist = query.get("q", [])

    if qlist and qlist[-1]:
        q = qlist[-1]
        show_id = urlparse(escape(q)).path.strip("/").split("/")[-1]
        context.update(q=q, **get_show_context(environ, show_id))

    return ResponseData(
        content=template.render(context).encode(),
        content_type="text/html; charset=utf-8",
    )


def get_rss(path: str) -> ResponseData:
    config = Config.load()
    spr = SPR(**config.__dict__)
    show_id = urlparse(escape(path)).path.strip("/").split("/")[-1]
    rss = spr.get_rss_by_show_id(show_id)

    if rss is None:
        return ResponseData(
            content=f"Show ID {show_id} not found".encode(),
            status="404 Not Found",
        )
    return ResponseData(
        content=rss,
        content_type="application/rss+xml; charset=utf-8",
    )


def application(environ: WSGIEnvironment, start_response: StartResponse):
    # http://wsgi.tutorial.codepoint.net/application-interface
    # https://www.toptal.com/python/pythons-wsgi-server-application-interface

    method = environ.get("REQUEST_METHOD", "").upper()
    path_components = path = environ.get("PATH_INFO", "").strip("/").split("/")
    path = path_components[0]

    if not path:
        response = get_index(environ=environ)
    elif path == "favicon.ico":
        response = ResponseData(status="404 Not Found")
    else:
        response = get_rss(path)

    response_headers = [
        ("Content-Type", response.content_type),
        ("Content-Length", str(len(response.content))),
    ]

    start_response(response.status, response_headers)

    if method == "HEAD":
        return []

    return [response.content]
