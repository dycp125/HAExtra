"""MiAI TTS Notification Service"""
import logging

import voluptuous as vol

from homeassistant.components.notify import (
    ATTR_DATA,
    PLATFORM_SCHEMA,
    BaseNotificationService,
)
from homeassistant.const import CONF_FILENAME, CONF_HOST, CONF_ICON
import homeassistant.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)


PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        # vol.Required(CONF_HOST): cv.string,
        # vol.Optional(CONF_FILENAME, default=WEBOSTV_CONFIG_FILE): cv.string,
        # vol.Optional(CONF_ICON): cv.string,
    }
)


def get_service(hass, config, discovery_info=None):
    """Return the notify service."""

    path = hass.config.path(config.get(CONF_FILENAME))
    # client = WebOsClient(config.get(CONF_HOST), key_file_path=path, timeout_connect=8)


    return MiAINotificationService()


class MiAINotificationService(BaseNotificationService):
    """Implement the notification service for LG WebOS TV."""

    def __init__(self):
        """Initialize the service."""

    def send_message(self, message="", **kwargs):
        """Send a message to the tv."""

        try:
            data = kwargs.get(ATTR_DATA)
        except:
            _LOGGER.error("Exception")