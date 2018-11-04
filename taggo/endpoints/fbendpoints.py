"""All the url endpoint hooks for facebook"""

import os
from sanic.response import json, text
from sanic import Blueprint
from .base import FacebookResponse
from taggo.parsers import FacebookYamlExecutor

VERIFY_TOKEN = os.environ.get("VF_TOKEN")
fb = Blueprint('facebook', url_prefix="/fb")

@fb.post('/recieve_message')
async def recieve_message(request):
    data = request.json 
    fb_resp = FacebookResponse(page_type=data["object"],
                               entries=data.get("entry"),
                               executor=request.app.config["command"])
    await fb_resp.send()
    return json({
        "reply": "success"
    })
                    
@fb.get("/recieve_message")
async def ping_pong(request):
    if request.raw_args.get("hub.verify_token") == VERIFY_TOKEN:
        return text(request.raw_args.get("hub.challenge"))
    else:
        return text("Error")

@fb.get('/')
async def ping(request):
    return text("Hi! Nice to meet you")