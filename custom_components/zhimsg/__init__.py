
# Logging
import logging
_LOGGER = logging.getLogger(__name__)

DOMAIN = 'zhimsg'


async def async_setup(hass, config):
    import importlib
    confs = config.get(DOMAIN)
    if confs:
        for conf in confs:
            platform = conf['platform']
            mod = importlib.import_module('.' + platform + 'msg', __package__)
            mod._hass = hass
            mod._conf = conf
            async_send = getattr(mod, 'async_send')
            SERVICE_SCHEMA = getattr(mod, 'SERVICE_SCHEMA')
            hass.services.async_register(
                DOMAIN, platform, async_send, schema=SERVICE_SCHEMA)
            _LOGGER.debug("Register service: %s.%s", DOMAIN, platform)
    return True
