from .base import YamlCommand, send_facebook_message, YamlExecutor
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FacebookCommand(YamlCommand):
    """Bot command for Facebook"""

    async def send(self, message, sender_id=None):
        res = await send_facebook_message(message, sender_id)
        logger.info(res)
        return res

class FacebookYamlExecutor(YamlExecutor):
    """Executing sequence of facebook commands"""
    command_class = FacebookCommand