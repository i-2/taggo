""" Getting yaml configuration files to work


requests:
  - name: sayhello
    pattern: hello
    webhook: http://api.hello.com
    method: get
    type: json
    text: hello
  
  - name: order tracking
    pattern: track\s+order\s+(?P<track>.*)?
    webhook: http://api.helloworld.com
    method: post
    type: json
    text: your order infomation {{response.description}}
    params: 
       - track

"""

import os
import re
import yaml
import json
import aiohttp
import logging
import inspect
from jinja2 import Template

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
        async with _method_attr(url, **_kwargs) as resp:
            json_response = await getattr(resp, RESPONSE_MIME_TYPES.get(content_type, "text"))()
            return json_response


async def send_facebook_message(sender_id, message):
    """Send the message to the particular id"""
    reply = await make_request(FACEBOOK_ACCESS_ENDPOINT, 
                               method="POST", payload={"recipient": {
                                   "id": sender_id
                               }, "message": {
                                   "text": message
                               }})
    return reply

class YamlCommand(object):
    
    def __init__(self, name, pattern,
                       webhook=None, method="GET",
                       response_type="json", text="", params=()):
        self.name = name
        self.pattern = re.compile(pattern)
        self.webhook_url = webhook
        self.method = method
        self.response_type = response_type
        self.text_template = text
        self.params = params
        
    def is_matched(self, msg):
        return True if self.pattern.match(msg) else False
        
    async def _send(self, data, sender_id=None):
        """await for request from webhook"""
        if self.webhook_url:
            payload = {}
            for key in self.params:
                payload[key] = data.get(key)
            response = await make_request(self.webhook_url,
                                          method=self.method,
                                          payload=payload)
            _template = Template(self.text_template)
            message = _template.render(response=response)
            if inspect.iscoroutinefunction(self.send):
                reply = await self.send(sender_id, message)
            else:
                reply = self.send(sender_id, message)
            return reply
        return None
        
    def parse(self, msg):
        """Parses the message and returns a dictionary
        of data's we are looking for"""
        parsed_content = {}
        match = self.pattern.match(msg)
        if not match:
            return None
        for key in self.params:
            parsed_content[key] = match.group(key)
        return parsed_content

    async def execute(self, msg, sender_id=None):
        if self.is_matched(msg):
            data = self.parse(msg)
            reply = await self._send(data, sender_id) 
            return reply
        else:
            return None
  
class YamlExecutor(object):
    
    command_class = YamlCommand

    def __init__(self, yaml_content):
        self.content = yaml.load(yaml_content)
        self._raw = yaml_content
        self.commands = []
        self.requests = self.content.get("requests", [])
        self.default_command = self._parse_command(self.content.get("default", {}))
        for command_dict in self.requests:
            self.commands.append(self._parse_command(command_dict))
    
    def _parse_command(self, command_dict):
        return self.command_class(command_dict.get("name"),
                           command_dict.get("pattern"),
                           webhook=command_dict.get("webhook"),
                           method=command_dict.get("method", "GET"),
                           response_type=command_dict.get("type", "json"),
                           text=command_dict.get("text", ""),
                           params=tuple(command_dict.get("params",())))

    @classmethod
    async def from_url(cls, url):
        response = await make_request(url, content_type="text")
        return cls(response)

    @classmethod
    def from_file(cls, f):
        content = f.read()
        return cls(content)
        
    async def respond(self, sender_id, msg):
        fil_gen = filter(lambda x: x.is_matched(msg), self.commands)
        matched = next(fil_gen)
        if matched:
            return await matched.execute(msg, sender_id=sender_id)
        else:
            return await self.default_command.execute(msg, sender_id=sender_id)