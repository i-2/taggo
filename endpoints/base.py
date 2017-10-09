
class FacebookResponse(object):

    def __init__(self, page_type="page", entries=[], executor=None):
        
        self.page_type = page_type
        self.entries = entries
        self.executor = executor

    async def send(self):
        """send the request and to facebook and recives the response"""

        if self.page_type != "page" and len(self.entries) > 0:
            return

        for entry in self.entries:
            for messaging_event in entry["messaging"]:
                msg = messaging_event.get("message", {})
                if "attachments" in msg:
                    break
                if msg:
                    sender_id = messaging_event["sender"]["id"]        
                    recipient_id = messaging_event["recipient"]["id"]  
                    message_text = messaging_event["message"]["text"]  
                    reply = await self.executor.respond(sender_id, message_text)  
        
