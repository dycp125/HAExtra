import logging
import time
import datetime

from miio import Device

import voluptuous as vol
import homeassistant.helpers.config_validation as cv

from homeassistant.const import CONF_HOST, CONF_NAME, CONF_TOKEN
from homeassistant.components.fan import FanEntity, SUPPORT_SET_SPEED, SUPPORT_OSCILLATE, SUPPORT_DIRECTION, PLATFORM_SCHEMA
from homeassistant.helpers.restore_state import RestoreEntity

_LOGGER = logging.getLogger(__name__)

CONF_MODEL = "model"

_MAPPING =
{
    'power': {'siid': 2, 'piid': 1}, 
    'power2': {'siid': 5, 'piid': 10}, 
    'power3': {'siid': 2, 'piid': 3}, 
    'power4': {'siid': 2, 'piid': 4}, 
    'power5': {'siid': 2, 'piid': 5}, 
    'power6': {'siid': 2, 'piid': 6}, 
    'power7': {'siid': 2, 'piid': 7}, 
    'power8': {'siid': 2, 'piid': 8}, 
    'power9': {'siid': 2, 'piid': 10}, 
    'powerA': {'siid': 2, 'piid': 11}, 
    'powerB': {'siid': 5, 'piid': 2}, 
    'powerC': {'siid': 6, 'piid': 1}, 
    'powerD': {'siid': 5, 'piid': 4}, 
    'powerE': {'siid': 5, 'piid': 5},
}

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_HOST): cv.string,
        vol.Required(CONF_TOKEN): vol.All(cv.string, vol.Length(min=32, max=32)),
        vol.Optional(CONF_NAME): cv.string,
        vol.Optional(CONF_MODEL): cv.string,
    }
)


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the light from config."""
    host = config[CONF_HOST]
    token = config[CONF_TOKEN]
    name = config.get(CONF_NAME)
    model = config.get(CONF_MODEL)
    add_entities([MiotFan(name, host, token)], True)


class MiotFan(FanEntity):

    def __init__(self, name, host, token):
        self._name = name or host
        self._device = MiotDevice(_MAPPING, host, token)
        self._status = {}
        self._state = None
        self._skip_update = False

    @property
    def supported_features(self):
        """Flag supported features."""
        return SUPPORT_SET_SPEED | SUPPORT_OSCILLATE | SUPPORT_DIRECTION

    @property
    def name(self):
        """Return the name of the device if any."""
        return self._name

    # @property
    # def icon(self):
    #     """Return the icon to use for device if any."""
    #     return 'mdi:washing-machine'

    @property
    def available(self):
        """Return true when state is known."""
        return self._state is not None

    @property
    def device_state_attributes(self):
        """Return the state attributes of the device."""
        return self._status

    def update(self):
        """Fetch state from the device."""
        if self._skip_update:
            self._skip_update = False
            return

        status = self._status
        try:
            for prop in WASHER_PROPS:
                status[prop] = self._device.send('get_prop', [prop])[0]
            self._state = status['wash_status'] == 1 and (
                (status['wash_process'] > 0 and status['wash_process'] < 7) or status['appoint_time'] != 0)
        except Exception as exc:
            _LOGGER.error("Error on update: %s", exc)
            self._state = None

    @property
    def is_on(self):
        """Return true if device is on."""
        return self._state

    def turn_on(self, speed=None, **kwargs):
        """Turn the device on."""
        _LOGGER.debug('turn_on: speed=%s, kwargs=%s', speed, kwargs)

    def turn_off(self, **kwargs):
        """Turn the device off."""
        pass

    @property
    def speed_list(self):
        """Get the list of available speeds."""
        return list(WASHER_PROGS.values())

    @property
    def speed(self):
        """Return the current speed."""
        return WASHER_PROGS.get(self._status.get('program'))

    def set_speed(self, speed):
        """Set the speed of the fan."""
        _LOGGER.debug('set_speed: %s', speed)

    @property
    def oscillating(self):
        """Return the oscillation state."""
        return bool(self._dry_mode)

    def oscillate(self, oscillating):
        """Oscillate the fan."""
        self._dry_mode = int(oscillating)
        _LOGGER.debug("oscillate: dry_mode=%s", self._dry_mode)

    @property
    def current_direction(self):
        """Return the current direction of the fan."""
        return 'reverse' if self._appoint_time else 'forward'

    def set_direction(self, direction):
        """Set the direction of the fan."""
        _LOGGER.debug("set_direction: appoint_time=%s", self._appoint_time)
