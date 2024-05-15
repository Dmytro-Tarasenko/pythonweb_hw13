import json
import re

from fastapi import Request, Response


# [Route(path='/openapi.json', name='openapi', methods=['GET', 'HEAD']),
# Route(path='/docs', name='swagger_ui_html', methods=['GET', 'HEAD']),
# Route(path='/docs/oauth2-redirect', name='swagger_ui_redirect', methods=['GET', 'HEAD']),
# Route(path='/redoc', name='redoc_html', methods=['GET', 'HEAD']),
# APIRoute(path='/contacts/', name='read', methods=['GET']),
# APIRoute(path='/contacts/{contact_id:int}', name='read_id', methods=['GET']),
# APIRoute(path='/contacts/', name='create', methods=['POST']),
# APIRoute(path='/contacts/find', name='find_contact', methods=['GET']),
# APIRoute(path='/contacts/bd_mates', name='get_birthday_mates_default', methods=['GET']),
# APIRoute(path='/contacts/bd_mates/{days:int}', name='get_birthday_mates', methods=['GET']),
# APIRoute(path='/contacts/{contact_id:int}/add/{field:str}/{value}', name='add_data', methods=['PUT']),
# APIRoute(path='/contacts/{contact_id:int}/edit/{field:str}/{value:str}', name='edit_data', methods=['PATCH']),
# APIRoute(path='/contacts/delete/{contact_id:int}', name='delete', methods=['DELETE']),
# APIRoute(path='/contacts/{contact_id:int}/delete/{field:str}', name='delete_data', methods=['DELETE']),
# APIRoute(path='/auth/register', name='new_user', methods=['POST']),
# APIRoute(path='/auth/login', name='login', methods=['POST']),
# APIRoute(path='/auth/refresh', name='refresh', methods=['POST']),
# APIRoute(path='/auth/logout', name='logout', methods=['POST']),
# APIRoute(path='/email/send-confirmation', name='send_confirmation', methods=['POST']),
# APIRoute(path='/email/confirm/{token:str}', name='confirm_email', methods=['GET']),
# APIRoute(path='/users/profile/', name='get_profile', methods=['GET']),
# APIRoute(path='/users/update-avatar/', name='update_avatar', methods=['PATCH']),
# APIRoute(path='/users/update-avatar/', name='update_avatar', methods=['POST']),
# APIRoute(path='/users/avatar', name='delete_avatar', methods=['DELETE']),
# APIRoute(path='/', name='index', methods=['GET'])]

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
        response_dict = json.loads(response_b)
        return_response = Response(content=response_b,
                        status_code=response.status_code,
                        headers=dict(response.headers),
                        media_type=response.media_type)

        return return_response

    return response
