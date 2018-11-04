import logging
from .response.base import apply_template
from .response.facebook import get_response
from .base import YamlCommand, YamlExecutor
from taggo.util.request import send_payload

logger = logging.getLogger(__name__)

class FacebookCommand(YamlCommand):
    """Bot command for Facebook"""

    async def send(self, response_dict, sender_id=None, webhook_response=None):
        """send data to respond"""
        applied_dict = apply_template(response_dict, response=webhook_response)
        payload_response = get_response(sender_id, applied_dict) 
        logger.info(payload_response)
        res = await send_payload(payload_response)
        return res


class FacebookYamlExecutor(YamlExecutor):
    """Executing sequence of facebook commands"""
    command_class = FacebookCommand