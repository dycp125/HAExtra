
# Logging
import logging
_LOGGER = logging.getLogger(__name__)

from homeassistant.components.notify import (
    ATTR_DATA,
    # PLATFORM_SCHEMA,
    BaseNotificationService,
)

# import voluptuous as vol
# import homeassistant.helpers.config_validation as cv
# PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
#     {
#         # vol.Required(CONF_HOST): cv.string,
#         # vol.Optional(CONF_FILENAME, default=WEBOSTV_CONFIG_FILE): cv.string,
#         # vol.Optional(CONF_ICON): cv.string,
#     }
# )

def get_service(hass, config, discovery_info=None):
    """Return the notify service."""
    return ZhiPlusNotificationService(hass, config["token"], config["secret"])


class ZhiPlusNotificationService(BaseNotificationService):
    """Implement the notification service for LG WebOS TV."""
    def __init__(self, hass, token, secret=None):
        """Initialize the service."""
        self._hass = hass
        self._token = token
        self._secret = secret

    async def async_send_message(self, message="", **kwargs):
        """Send a message."""
        try:
            data = kwargs.get(ATTR_DATA)
            await self.async_send(message)
        except:
            import traceback
            _LOGGER.error(traceback.format_exc())

    async def  async_send(self, message):
        url = "https://oapi.dingtalk.com/robot/send?access_token=" + self._token
        if self._secret is not None:
            import time
            import hmac
            import hashlib
            import base64
            import urllib
            timestamp = round(time.time() * 1000)
            hmac_code = hmac.new(self._secret.encode('utf-8'), '{}\n{}'.format(timestamp, self._secret).encode('utf-8'), digestmod=hashlib.sha256).digest()
            sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
            url += '&timestamp=' + str(timestamp) + '&sign=' + sign

        session = self._hass.helpers.aiohttp_client.async_get_clientsession()
        _LOGGER.debug("URL: %s", url)
        async with session.post(url, json={'msgtype': 'text', 'text': {'content': message}}) as response:
            json = await response.json()
            if json['errcode'] != 0:
                _LOGGER.error("RESPONSE: %s", await response.text())
