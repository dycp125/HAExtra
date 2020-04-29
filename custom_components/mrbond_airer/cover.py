"""Support for MrBond Airer."""
import logging

from miio import Device
import voluptuous as vol
import homeassistant.helpers.config_validation as cv

from homeassistant.components.cover import CoverDevice, PLATFORM_SCHEMA, ATTR_POSITION
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_TOKEN
from homeassistant.helpers.event import async_call_later

_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_HOST): cv.string,
        vol.Required(CONF_TOKEN): vol.All(cv.string, vol.Length(min=32, max=32)),
        vol.Optional(CONF_NAME): cv.string,
    }
)

AIRER_PROPS = [
            "dry",
            "led",
            "motor",
            "drytime",
            "airer_location",
]

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the light from config."""
    host = config[CONF_HOST]
    token = config[CONF_TOKEN]
    name = config.get(CONF_NAME)
    add_entities([MrBondAirer(name, host, token)], True)


class MrBondAirer(CoverDevice):
    """Representation of a cover."""

    def __init__(self, name, host, token):
        """Initialize the light device."""
        self._name = name or host
        self._device = Device(host, token)
        self._state = None
        self._status = {}
        self._skip_update = False

    @property
    def name(self):
        """Return the name of the device if any."""
        return self._name

    @property
    def icon(self):
        """Return the name of the device if any."""
        return 'mdi:hanger'

    # @property
    # def available(self):
    #     """Return true when state is known."""
    #     return self._state is not None

    @property
    def device_state_attributes(self):
        """Return the state attributes of the device."""
        return self._status

    def update(self):
        """Fetch state from the device."""
        if self._skip_update:
            self._skip_update = False
            return

        try:
            for prop in AIRER_PROPS:
                self._status[prop] = self._device.send('get_prop', [prop])[0]
        except Exception as exc:
            _LOGGER.error("Error on update: %s", exc)
            self._status = {}

    def send(self, name, value, success=['ok']):
        try:
            result = self._device.send(name, [value])
            _LOGGER.debug("Response received from miio device: %s", result)
            return result == success
        except Exception as exc:
            #import traceback
            # _LOGGER.error(traceback.format_exc())
            _LOGGER.error("Error on miio: %s", exc)
            return None

    @property
    def current_cover_position(self):
        """Return current position of cover.

        None is unknown, 0 is closed, 100 is fully open.
        """
        return self._status.get('airer_location') or 10

    @property
    def is_opening(self):
        """Return if the cover is opening or not."""
        return self._status.get('motor') == '1'

    @property
    def is_closing(self):
        """Return if the cover is closing or not."""
        return self._status.get('motor') == '2'

    @property
    def is_closed(self):
        """Return if the cover is closed or not."""
        return self._status.get('airer_location')

    def open_cover(self, **kwargs):
        """Open the cover."""
        _LOGGER.warn("open_cover: %s", kwargs)
        self.send('set_motor', 1)
        pass

    def close_cover(self, **kwargs):
        """Close cover."""
        _LOGGER.warn("close_cover: %s", kwargs)
        self.send('set_motor', 2)
        pass

    def stop_cover(self, **kwargs):
        """Stop the cover."""
        self.send('set_motor', 0)

    def set_cover_position(self, **kwargs):
        """Move the cover to a specific position."""
        _LOGGER.warn("set_cover_position: %s", kwargs)
        location = self._status.get('airer_location')
        position = kwargs.get(ATTR_POSITION)
        if location > position:
            delay = location - position / 10
            open_cover()
        else:
            delay = position - location / 10
            close_cover()
        async_call_later(self._hass, delay, self.stop_cover)
