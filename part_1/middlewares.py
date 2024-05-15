import json
import re

from fastapi import Request, Response


async def define_response(request: Request,
                          call_next):
    browser_regexp = (r"Mozilla|Chrome|Chromium|Apple|WebKit|" +
                      r"Edge|IE|MSIE|Firefox|Gecko")
    docs_redoc_regexp = (r"/docs$|/docs#|/docs/|/redoc$|/redoc#|/redoc/"
                         + r"|/openapi.json$|/static/|/favicon.ico$")

    swagger_static_match = re.search(pattern=docs_redoc_regexp,
                                     string=str(request.url),
                                     flags=re.I)
    ua_string = request.headers.get('user-agent')
    browser_match = re.search(browser_regexp, ua_string)
    response_type = "api"
    if swagger_static_match is None:
        if browser_match:
            response_type = "html"
    response = await call_next(request)
    content_type = response.headers.get('content-type')
    content_json = re.match(r"application/json", content_type)
    if all([response_type == "html",
            content_json]):
        print(response_type)
        print(request.url.path, request.url.query)
        print(response.headers)
        response_b = b""
        async for chunk in response.body_iterator:
            response_b += chunk
        print(json.loads(response_b)['detail'])
        return Response(content=response_b,
                        status_code=response.status_code,
                        headers=dict(response.headers),
                        media_type=response.media_type)
    return response
