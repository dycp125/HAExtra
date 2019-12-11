
# Logging
import logging
_LOGGER = logging.getLogger(__name__)

DOMAIN = 'dingding'

# 
from homeassistant.components.http import HomeAssistantView
from homeassistant.helpers.state import AsyncTrackStates

# Config
import voluptuous as vol
import homeassistant.helpers.config_validation as cv

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Required('senderId'): cv.string,
        }),
    }, extra=vol.ALLOW_EXTRA)

# 
_hass = None
_senderId = None

#
async def async_setup(hass, config):
    global _hass, _senderId
    _hass = hass
    conf = config[DOMAIN]
    _senderId = conf['senderId']
    _LOGGER.debug("%s,%s", config, _senderId)
    hass.http.register_view(DingDingView)
    return True

#
class DingBotView(ChatBotView):
    name = DOMAIN

    def response(self, answer):
        return {"msgtype": "text", "text": {"content": answer}}

    def check(self, data):
        #_LOGGER.debug("TOKEN: <%s>~=<%s>", data['senderId'], _senderId)
        return data['senderId'] == _senderId

    async def handle(self, data):
        return await hassQuery(data['text']['content'])
