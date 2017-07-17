from .base import YamlCommand, send_facebook_message, YamlExecutor

class FacebookCommand(YamlCommand):
    """Bot command for Facebook"""

    async def send(self, message, sender_id=None):
        res = await send_facebook_message(message, sender_id)
        return res

class FacebookYamlExecutor(YamlExecutor):
    """Executing sequence of facebook commands"""
    command_class = FacebookCommand