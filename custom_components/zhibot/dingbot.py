
#
from .zhibot import zhibotQuery
from .chatbot import chatbotView

# Logging
import logging
_LOGGER = logging.getLogger(__name__)


#
class dingbotView(chatbotView):

    def check(self, data):
        if data['chatbotUserId'] in self.conf:
            return True
        return super().check(data)

    def config_done(self, data):
        self.conf.append(data['chatbotUserId'])

    def config_desc(self, data):
        return "钉钉群“%s”的“%s”正在试图访问“%s”。" % (data['conversationTitle'], data['senderNick'], data['text']['content'])

    async def handle(self, data):
        return await zhibotQuery(data['text']['content'])

    def response(self, answer):
        return {'msgtype': 'text', 'text': {'content': answer}}
