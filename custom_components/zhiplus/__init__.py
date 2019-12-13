
# Logging
import logging
_LOGGER = logging.getLogger(__name__)

DOMAIN = 'zhiplus'

#
async def async_setup(hass, config):
	import importlib
    bots = config[DOMAIN]
    for bot in bots:
    	_LOGGER.debug("Loading Zhi+ bot %s", bot['platform'])
    	mod = importlib.import_module('.' + bot['platform'], __package__)
    	await mod.async_setup(hass, bot)
    	# mod._hass = hass
    	# hass.http.register_view(mod.ChatBotView)
    return True
