import aiohttp

# Logging
import logging
_LOGGER = logging.getLogger(__name__)

# Config validation
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
SERVICE_SCHEMA = vol.Schema({
    vol.Required('message'): cv.string,
})

# Global variable
_hass = None
_conf = None


async def async_send(call):
    token = _conf['token']
    secret = _conf.get('secret')
    message = call.data['message']
    url = "https://oapi.dingtalk.com/robot/send?access_token=" + token
    if secret is not None:
        import time
        import hmac
        import hashlib
        import base64
        import urllib
        timestamp = round(time.time() * 1000)
        hmac_code = hmac.new(secret.encode('utf-8'), '{}\n{}'.format(
            timestamp, secret).encode('utf-8'), digestmod=hashlib.sha256).digest()
        sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
        url += '&timestamp=' + str(timestamp) + '&sign=' + sign

    _LOGGER.debug("URL: %s", url)
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json={'msgtype': 'text', 'text': {'content': message}}) as response:
            json = await response.json()
            if json['errcode'] != 0:
                _LOGGER.error("RESPONSE: %s", await response.text())
