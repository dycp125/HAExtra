
#
from .zhibot import zhibotQuery
from .chatbot import chatbotView

# Logging
import logging
_LOGGER = logging.getLogger(__name__)

#
_hass = None
_conf = None


#
class dingbotView(chatbotView):

    def check(self, data):
        return data['chatbotUserId'] == _conf['chatbotUserId']

    async def handle(self, data):
        return await zhibotQuery(_hass, data['text']['content'])

    def response(self, answer):
        return {'msgtype': 'text', 'text': {'content': answer}}
