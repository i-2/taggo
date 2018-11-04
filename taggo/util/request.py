"""request.py"""

import os
import aiohttp
import json

FACEBOOK_ACCESS_ENDPOINT = "https://graph.facebook.com/v2.6/me/messages?access_token={}".format(os.environ.get("ACCESS_TOKEN"))
RESPONSE_MIME_TYPES = {
    "json": "json",
}

class TaggoParserException(Exception):
    """Base Exception class"""
    pass


async def make_request(url,
                       method="GET",
                       payload=None,
                       content_type="json",
                       loop=None):
    """Makes an http request to the resources specified
    
    Args: 
      - url : specified url
      - method: http method to use
      - payload: payload information
      - content_type: ContentType meta data
      - loop: Event loop to run on
      
    Returns:
      - response from the resource
    
    """
    
    async with aiohttp.ClientSession(loop=loop) as session:
        _method_attr = getattr(session, method.lower())
        _kwargs = {"params" if method.lower() == "get" else "data": payload}
        if content_type == "json":
            _kwargs.update({
                "headers": {"Content-Type": "application/json"} 
            })
        async with _method_attr(url, verify_ssl=False, **_kwargs) as resp:
            response = await getattr(resp, RESPONSE_MIME_TYPES.get(content_type, "text"))()
            return response


async def send_payload(payload):
    """Send the message to the particular id"""
    reply = await make_request(FACEBOOK_ACCESS_ENDPOINT,
                               method="POST", payload=json.dumps(payload))
    return reply