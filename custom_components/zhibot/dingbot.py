
#
from .zhibot import zhibotQuery
from .chatbot import chatbotView
from homeassistant.util.json import load_json, save_json

# Logging
import logging
_LOGGER = logging.getLogger(__name__)

#
_hass = None
_conf = None


#
class dingbotView(chatbotView):

    def __init__(self):
        self._conf = load_json(_hass.config.path('.dingbot'))
        if not self._conf:
            self._conf = []
        self._configuring = None
        super().__init__()

    def check(self, data):
        chatbotUserId = data['chatbotUserId']
        if chatbotUserId in self._conf:
            return True
        self.config(data)
        return False

    async def handle(self, data):
        return await zhibotQuery(_hass, data['text']['content'])

    def response(self, answer):
        return {'msgtype': 'text', 'text': {'content': answer}}

    def config(self, data):
        configurator = _hass.components.configurator
        if self._configuring:
            configurator.async_request_done(self._configuring)

        def config_done(fields):
            configurator.request_done(self._configuring)
            self._configuring = None

            _LOGGER.debug(fields)
            if fields.get('agree') == 'ok':
                self._conf.append(data['chatbotUserId'])
                save_json(_hass.config.path('.dingbot'), self._conf)

        self._configuring = _hass.components.configurator.async_request_config(
            '智加加', config_done,
            description="钉钉群“%s”的“%s”正在试图访问“%s”。" % (data['conversationTitle'], data['senderNick'], data['text']['content']),
            submit_caption='完成',
            fields=[{'id': 'agree', 'name': '如果允许访问，请输入“ok”'}],
        )
