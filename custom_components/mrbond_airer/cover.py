"""Support for MrBond Airer."""
import logging

from miio import Device
import voluptuous as vol
import homeassistant.helpers.config_validation as cv

from homeassistant.components.cover import CoverDevice, PLATFORM_SCHEMA, ATTR_POSITION
from homeassistant.components.light import Light
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
            # "drytime",
            # "airer_location",
]

AIRER_DURATION = 10

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the light from config."""
    host = config[CONF_HOST]
    token = config[CONF_TOKEN]
    name = config.get(CONF_NAME) or host

    device = Device(host, token)

    add_entities([
        MrBondAirer(hass, name, device),
        MrBondLight(hass, name + '灯', device),
        ], True)



class MiioEntity():
    """Representation of MrBond Airer Light."""

    def __init__(self, hass, name, device):
        """Initialize the light device."""
        self._hass = hass
        self._name = name
        self._device = device
        self._status = {}
        self._available = False

    @property
    def name(self):
        """Return the name of the device if any."""
        return self._name

    @property
    def available(self):
        """Return true when state is known."""
        return self._available

    @property
    def device_state_attributes(self):
        """Return the state attributes of the device."""
        return self._status

    def update(self):
        """Fetch state from the device."""
        try:
            for prop in AIRER_PROPS:
                self._status[prop] = self._device.send('get_prop', [prop])[0]
            self._available = True
        except Exception as exc:
            _LOGGER.error("Error on update: %s", exc)
            self._available = False

    def control(self, name, value):
        try:
            result = self._device.send(name, [value])
            _LOGGER.debug("Response from miio control: %s", result)
            return result == ['ok']
        except Exception as exc:
            #import traceback
            # _LOGGER.error(traceback.format_exc())
            _LOGGER.error("Error on miio control: %s", exc)
            #self.available = False
            return None


class MrBondLight(MiioEntity, Light):
    """Representation of MrBond Airer Light."""

    @property
    def is_on(self):
        """Return true if light is on."""
        return self._status.get('led') == '1'

    def turn_on(self, **kwargs):
        """Turn the light on."""
        if self.control('set_led', 1):
            self._status['led'] = '1'

    def turn_off(self, **kwargs):
        """Turn the light off."""
        if self.control('set_led', 0):
            self._status['led'] = '0'


class MrBondAirer(MiioEntity, CoverDevice):
    """Representation of a cover."""

    def __init__(self, hass, name, device):
        """Initialize the light device."""
        super().__init__(hass, name ,device)
        self._status['airer_location'] = '1'

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
        location = self._status.get('airer_location')
        return 0 if location == '2' else (50 if location == '0' else 100)

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
        return self._status.get('airer_location') == '2'

    def open_cover(self, **kwargs):
        """Open the cover."""
        _LOGGER.warn("open_cover: %s", kwargs)
        if self.control('set_motor', 1):
            self._status['airer_location'] == '1'

    def close_cover(self, **kwargs):
        """Close cover."""
        _LOGGER.warn("close_cover: %s", kwargs)
        if self.control('set_motor', 2):
            self._status['airer_location'] == '2'

    def stop_cover(self, **kwargs):
        """Stop the cover."""
        if self.control('set_motor', 0):
            self._status['motor'] == '0'
            self._status['airer_location'] == '0'

    def set_cover_position(self, **kwargs):
        """Move the cover to a specific position."""
        _LOGGER.warn("set_cover_position: %s", kwargs)
        position = kwargs.get(ATTR_POSITION)
        if position <= 0:
            self.close_cover()
        elif position >= 100:
            self.open_cover()
        else:
            location = self._status.get('airer_location')
            if location == '1':
                self.close_cover()
                self._status['motor'] == '2'
            elif location == '2':
                self.open_cover()
                self._status['motor'] == '1'
            else:
                return
            async_call_later(self._hass, 5, self.stop_cover)

    # def listen_cover(self):
    #     if self._untrack_utc_time_change is None:
    #         self._untrack_utc_time_change = track_utc_time_change(self._hass, track_time_changed)

    # def stop_listen_cover(self):
    #     if self._untrack_utc_time_change is not None:
    #         self._untrack_utc_time_change()
    #         self._untrack_utc_time_change = None

    # def track_time_changed(self, now):
    #     motor = self._status['motor']
    #     step = 100 / AIRER_DURATION
    #     if motor == '1':
    #         self._location += step
    #     elif motor == '2'
    #         self._location -= step

    #     if self._location <= 0:
    #         self._location = 0
    #         stop_cover()
    #     elif self._location >= 100:
    #         self._location = 100
    #         stop_cover()

    #     self.schedule_update_ha_state()