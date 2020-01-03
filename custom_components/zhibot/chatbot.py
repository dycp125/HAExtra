
from homeassistant.components.http import HomeAssistantView
from homeassistant.util.json import load_json, save_json
from homeassistant.components.http import KEY_HASS

# Logging
import logging
_LOGGER = logging.getLogger(__name__)


class chatbotView(HomeAssistantView):
    """View to handle Configuration requests."""

    def __init__(self):
        self.name = self.__class__.__name__.rstrip('View').lower()
        self.url = '/' + self.name
        self.requires_auth = False

        self._configuring = None
        self.conf = None

    async def post(self, request):
        try:
            #request[KEY_REAL_IP], request.query
            hass = request.app[KEY_HASS]
            if self.conf is None:
                self.conf = load_json(hass.config.path('.' + self.name))
                if not self.conf:
                    self.conf = []

            data = await request.json()
            _LOGGER.debug("REQUEST: %s", data)
            answer = await self.handle(hass, data) if self.check(hass, data) else "没有访问授权！"
        except:
            import traceback
            _LOGGER.error(traceback.format_exc())
            answer = "程序出错啦！"
        _LOGGER.debug("RESPONSE: %s", answer)
        return self.json(self.response(answer))

    def response(self, answer):
        return None

    async def handle(self, hass, data):
        return "未能处理"

    def check(self, hass, data):
        configurator = hass.components.configurator
        if self._configuring:
            configurator.async_request_done(self._configuring)

        def config_callback(fields):
            configurator.request_done(self._configuring)
            self._configuring = None

            _LOGGER.debug(fields)
            if fields.get('agree') == 'ok':
                self.config_done(data)
                save_json(hass.config.path('.' + self.name), self.conf)

        self._configuring = configurator.async_request_config(
            '智加加', config_callback,
            description=self.config_desc(data),
            submit_caption='完成',
            fields=[{'id': 'agree', 'name': '如果允许访问，请输入“ok”'}],
        )
        return False

    def config_done(self, data):
        pass

    def config_desc(self, data):
        return "授权访问"
