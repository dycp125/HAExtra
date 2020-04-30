"""Support for MrBond Airer."""
import logging

import voluptuous as vol
import homeassistant.helpers.config_validation as cv

from homeassistant.components.cover import CoverDevice, PLATFORM_SCHEMA, ATTR_POSITION
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_TOKEN
from homeassistant.helpers.event import async_call_later

from . import MiioEntity, DOMAIN

_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_HOST): cv.string,
        vol.Required(CONF_TOKEN): vol.All(cv.string, vol.Length(min=32, max=32)),
        vol.Optional(CONF_NAME): cv.string,
    }
)

AIRER_DURATION = 10

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the light from config."""
    host = config[CONF_HOST]
    token = config[CONF_TOKEN]
    name = config.get(CONF_NAME) or host

    device = Device(host, token)

    add_entities([MrBondAirer(hass, name, device)], True)


# class MrBondLight(MiioEntity, Light):
#     """Representation of MrBond Airer Light."""

#     @property
#     def is_on(self):
#         """Return true if light is on."""
#         return self._device.status.get('led') == '1'

#     def turn_on(self, **kwargs):
#         """Turn the light on."""
#         if self._device.control('set_led', 1):
#             self._device.status['led'] = '1'

#     def turn_off(self, **kwargs):
#         """Turn the light off."""
#         if self._device.control('set_led', 0):
#             self._device.status['led'] = '0'


class MrBondAirer(MiioEntity, CoverDevice):
    """Representation of a cover."""

    def __init__(self, hass, name, device):
        """Initialize the light device."""
        super().__init__(hass, name ,device)
        self._device.status['airer_location'] = '1'

    @property
    def icon(self):
        """Return the name of the device if any."""
        return 'mdi:hanger'

    @property
    def should_poll(self):
        """Return True if entity has to be polled for state.

        False if entity pushes its state to HA.
        """
        return False

    @property
    def current_cover_position(self):
        """Return current position of cover.

        None is unknown, 0 is closed, 100 is fully open.
        """
        location = self._device.status.get('airer_location')
        return 0 if location == '2' else (50 if location == '0' else 100)

    @property
    def is_opening(self):
        """Return if the cover is opening or not."""
        return self._device.status.get('motor') == '1'

    @property
    def is_closing(self):
        """Return if the cover is closing or not."""
        return self._device.status.get('motor') == '2'

    @property
    def is_closed(self):
        """Return if the cover is closed or not."""
        return self._device.status.get('airer_location') == '2'

    def open_cover(self, **kwargs):
        """Open the cover."""
        _LOGGER.warn("open_cover: %s", kwargs)
        if self._device.control('set_motor', 1):
            self._device.status['airer_location'] == '1'

    def close_cover(self, **kwargs):
        """Close cover."""
        _LOGGER.warn("close_cover: %s", kwargs)
        if self._device.control('set_motor', 2):
            self._device.status['airer_location'] == '2'

    def stop_cover(self, **kwargs):
        """Stop the cover."""
        if self._device.control('set_motor', 0):
            self._device.status['motor'] == '0'
            self._device.status['airer_location'] == '0'

    def set_cover_position(self, **kwargs):
        """Move the cover to a specific position."""
        _LOGGER.warn("set_cover_position: %s", kwargs)
        position = kwargs.get(ATTR_POSITION)
        if position <= 0:
            self.close_cover()
        elif position >= 100:
            self.open_cover()
        else:
            location = self._device.status.get('airer_location')
            if location == '1':
                self.close_cover()
                self._device.status['motor'] == '2'
            elif location == '2':
                self.open_cover()
                self._device.status['motor'] == '1'
            else:
                return
            async_call_later(self._hass, 5, self.stop_cover)
