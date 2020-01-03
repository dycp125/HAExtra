
# Logging
import logging
_LOGGER = logging.getLogger(__name__)

DOMAIN = 'zhibot'
hass = None


async def async_setup(_hass, config):
    global hass
    hass = _hass
    import importlib
    confs = config.get(DOMAIN)
    if confs:
        http = config.get('http')
        base_url = http.get('base_url', '') if http else ''
        for conf in confs:
            platform = conf['platform'] + 'bot'
            mod = importlib.import_module('.' + platform, __package__)
            hass.http.register_view(getattr(mod, platform + 'View'))
            _LOGGER.debug("Listing on: %s/%s", base_url, platform)
    return True
