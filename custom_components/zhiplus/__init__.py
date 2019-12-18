
# Logging
import logging
_LOGGER = logging.getLogger(__name__)

DOMAIN = 'zhiplus'

#
import importlib
async def async_setup(hass, config):
    confs = config[DOMAIN]
    for conf in confs:
        platform = conf['platform']
        _LOGGER.debug("Loading Zhi+ %s", platform)
        mod = importlib.import_module('.' + platform, __package__)
        mod._hass = hass
        mod._conf = conf
        hass.http.register_view(getattr(mod, platform + 'View'))
    return True
