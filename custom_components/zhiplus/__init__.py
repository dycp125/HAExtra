
# Logging
import logging
_LOGGER = logging.getLogger(__name__)

DOMAIN = 'zhiplus'


async def async_setup(hass, config):
    import importlib
    confs = config.get(DOMAIN)
    if confs:
        for conf in confs:
            platform = conf['platform']
            _LOGGER.debug("Loading Zhi+ %s", platform)
            mod = importlib.import_module('.' + platform, __package__)
            mod._hass = hass
            mod._conf = conf
            hass.http.register_view(getattr(mod, platform + 'View'))
    return True
