
# Logging
import importlib
from homeassistant.components.notify import (
    ATTR_DATA,
    ATTR_TARGET,
    # PLATFORM_SCHEMA,
    BaseNotificationService,
)

import logging
_LOGGER = logging.getLogger(__name__)

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
    return ZhiPlusNotificationService(config['targets'])


class ZhiPlusNotificationService(BaseNotificationService):
    """Implement the notification service."""

    def __init__(self, targets):
        """Initialize the service."""
        self._targets = targets

    @property
    def targets(self):
        return self._targets

    async def async_send_message(self, message="", **kwargs):
        """Send a message."""
        try:
            conf = kwargs.get(ATTR_TARGET)[0]
            data = kwargs.get(ATTR_DATA)
            target = conf['target']
            mod = importlib.import_module('.' + target + 'tify', __package__)
            async_send = getattr(mod, 'async_send')
            await async_send(conf, message, data)
        except:
            import traceback
            _LOGGER.error(traceback.format_exc())
