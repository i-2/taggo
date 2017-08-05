"""Facebook bot response class"""

import json
from .base import make_request, FACEBOOK_ACCESS_ENDPOINT
from jinja2 import Template


class FacebookBotResponse(dict):
    """responding to facebook bot"""

    MESSAGE_TYPE = None

    def __init__(self, raw_dict, recipient):
        self._response = raw_dict
        self._recipient = recipient
        super(FacebookBotResponse, self).__init__()
        self._construct_payload()

    def payload(self):
        """Helps constructing payload"""
        raise NotImplementedError("Not implemented")

    def _construct_payload(self):
        """construct the payload pocket"""
        self["recipient"] = {"id": self._recipient}
        self["message"] = self.payload()

    async def send(self):
        """sending response to servers"""
        reply = await make_request(FACEBOOK_ACCESS_ENDPOINT,
                                   method="POST",
                                   payload=json.dumps(self))
        return reply

    @classmethod
    def is_of(cls, typ):
        """is type of"""
        return cls.MESSAGE_TYPE == typ


class TextBotResponse(FacebookBotResponse):
    """Text Response from bot"""

    MESSAGE_TYPE = "text"

    def payload(self):
        return dict(text=self._response.get("text"))


class TemplateResponse(FacebookBotResponse):
    """Template response"""

    MESSAGE_TYPE = "template"
    TEMPLATE_TYPE = None

    def __init__(self, *args, **kwargs):
        super(TemplateResponse, self).__init__(*args, **kwargs)

    def payload(self):
        _payload = {"template_type": self.__class__.TEMPLATE_TYPE}
        _payload.update(**self.render())
        return {"attachment": {
                     "type": self.__class__.MESSAGE_TYPE, 
                     "payload": _payload
                 }}

    def render(self):
        """to be used by child"""
        raise NotImplementedError()

    @classmethod
    def is_templateof(cls, temp):
        return cls.TEMPLATE_TYPE == temp

class WebViewTemplate(TemplateResponse):
    """Adding webview template"""
    TEMPLATE_TYPE = "generic"

    def render(self):
        return dict(elements=self._response.get("elements", []))


class ListTemplate(WebViewTemplate):
    """Adding list template"""
    TEMPLATE_TYPE = "list"


def get_response(recipient, response):
    """get the appropriate response object"""

    _type = response.get("type")
    _tt = response.get("template_type", "generic")

    if _type == "text":
        return TextBotResponse(response, recipient)
    elif  _type == "template":
        if _tt == "generic":
            return WebViewTemplate(response, recipient)
        elif _tt == "list":
            return ListTemplate(response, recipient)
    return None

def apply_template(dicty, **kwds):
    """apply templating recursively"""
    new_dicty = dicty.copy()
    for key, value in new_dicty.items():
        if isinstance(value, dict):
            new_dicty[key] = apply_template(value)
        elif isinstance(value, str):
            _template = Template(value)
            new_dicty[key] = _template.render(**kwds)
    return new_dicty