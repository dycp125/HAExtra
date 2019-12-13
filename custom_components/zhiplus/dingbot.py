
# Logging
import logging
_LOGGER = logging.getLogger(__name__)

DOMAIN='dinbot'

# # 
_hass = None
_senderId = None

#
async def async_setup(hass, config):
    global _hass, _senderId
    _hass = hass
    _senderId = config['senderId']
    _LOGGER.debug("%s", _senderId)
    hass.http.register_view(DingBotView)
    return True

#
from .zhibot import zhibotQuery
from .chatbot import ChatBotView

#
class DingBotView(ChatBotView):
    name = DOMAIN

    def response(self, answer):
        return {"msgtype": "text", "text": {"content": answer}}

    def check(self, data):
        #_LOGGER.debug("TOKEN: <%s>~=<%s>", data['senderId'], _senderId)
        return data['senderId'] == _senderId

    async def handle(self, data):
        return await zhibotQuery(_hass, data['text']['content'])
