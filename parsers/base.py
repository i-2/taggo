""" Getting yaml configuration files to work


requests:
  - name: sayhello
    pattern: hello
    webhook: http://api.hello.com
    method: get
    type: json
    response:
       text: hello
  
  - name: order tracking
    pattern: track\s+order\s+(?P<track>.*)?
    webhook: http://api.helloworld.com
    method: post
    type: json
    response:
       text: your order infomation {{response.description}}
    params: 
       - track

"""

import os
import re
import yaml
import json
import aiohttp
import logging as logger
import inspect


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
        async with _method_attr(url, **_kwargs) as resp:
            response = await getattr(resp, RESPONSE_MIME_TYPES.get(content_type, "text"))()
            return response


async def send_payload(payload):
    """Send the message to the particular id"""
    logger.info(payload)
    reply = await make_request(FACEBOOK_ACCESS_ENDPOINT,
                               method="POST", payload=json.dumps(payload))
    return reply

class YamlCommand(object):
    
    def __init__(self, name, pattern,
                       webhook=None, method="GET",
                       response_type="json", response=None, params=(), ignore_case=True):
        self.name = name
        self.pattern = re.compile(pattern)
        self.webhook_url = webhook
        self.method = method
        self.response_type = response_type
        self.params = params
        self.ignore_case = ignore_case
        self._response = response
                
    def is_matched(self, msg):
        message = msg.lower() if self.ignore_case else msg
        return True if self.pattern.match(message) else False
        
    async def _send(self, data, sender_id=None):
        """await for request from webhook"""
        payload = {}
        for key in self.params:
            payload[key] = data.get(key)
        response = None
        if self.webhook_url:
            response = await make_request(self.webhook_url,
                                          method=self.method,
                                          payload=payload,
                                          content_type=self.response_type)
        # _template = Template(self.text_template)
        # logger.info(response)
        # message = _template.render(response=response)
        if inspect.iscoroutinefunction(self.send):
            reply = await self.send(self._response, sender_id, webhook_response=response)
        else:
            reply = self.send(self._response, sender_id, webhook_response=response)
        return reply

        
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
        logger.info(self._raw)
        for command_dict in self.requests:
            logger.info(command_dict)
            self.commands.append(self._parse_command(command_dict))

    def _parse_command(self, command_dict):
        return self.command_class(command_dict.get("name"),
                           command_dict.get("pattern"),
                           webhook=command_dict.get("webhook"),
                           method=command_dict.get("method", "GET"),
                           response_type=command_dict.get("type", "json"),
                           response=command_dict.get("response", ""),
                           params=tuple(command_dict.get("params",())),
                           ignore_case=command_dict.get("ignorecase", True))

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
        try:
            matched = next(fil_gen)
            logger.info(getattr(matched, 'name', 'None'))
            if matched:
                return await matched.execute(msg, sender_id=sender_id)
            else:
                return await self.default_command.execute(msg, sender_id=sender_id)
        except StopIteration:
            return await self.default_command.execute(msg, sender_id=sender_id)