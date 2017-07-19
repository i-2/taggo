"""All the url endpoint hooks for facebook"""

import os
from sanic.response import json, text
from sanic import Blueprint
from parsers import FacebookYamlExecutor

VERIFY_TOKEN = os.environ.get("VF_TOKEN")
fb = Blueprint('facebook', url_prefix="/fb")

@fb.post('/recieve_message')
async def recieve_message(request):
    data = request.json
    if data["object"] == "page":
        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:
                if messaging_event.get("message"):  
                    sender_id = messaging_event["sender"]["id"]        
                    recipient_id = messaging_event["recipient"]["id"]  
                    message_text = messaging_event["message"]["text"]  
                    executor = request.app.config["command"]
                    reply = await executor.execute(message_text, sender_id=sender_id) 
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