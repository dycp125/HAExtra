
# Logging
import logging
_LOGGER = logging.getLogger(__name__)

#
_hass = None
_conf = None

#
from .zhibot import zhibotQuery
from .chatbot import ChatBotView

#
class dingbotView(ChatBotView):

    def response(self, answer):
        return {"msgtype": "text", "text": {"content": answer}}

    def check(self, data):
        #_LOGGER.debug("TOKEN: <%s>~=<%s>", data['senderId'], _senderId)
        return data['senderId'] == _conf['senderId']

    async def handle(self, data):
        return await zhibotQuery(_hass, data['text']['content'])
