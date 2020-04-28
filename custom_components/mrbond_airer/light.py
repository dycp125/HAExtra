"""Support for MrBond Airer's Light."""
import logging

from miio import Device
import voluptuous as vol
import homeassistant.helpers.config_validation as cv

from homeassistant.components.light import Light, PLATFORM_SCHEMA
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_TOKEN

_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_HOST): cv.string,
        vol.Required(CONF_TOKEN): vol.All(cv.string, vol.Length(min=32, max=32)),
        vol.Optional(CONF_NAME): cv.string,
    }
)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the light from config."""
    host = config[CONF_HOST]
    token = config[CONF_TOKEN]
    name = config.get(CONF_NAME)
    async_add_entities([MrBondLight(name, host, token)], True)


class MrBondLight(Light):
    """Representation of MrBond Airer Light."""

    def __init__(self, name, host, token):
        """Initialize the light device."""
        self._name = name or host
        self._device = Device(host, token)
        self._state = None

    @property
    def name(self):
        """Return the name of the device if any."""
        return self._name

    @property
    def available(self):
        """Return true when state is known."""
        return self._state is not None

    @property
    def is_on(self):
        """Return true if light is on."""
        return self._state

    async def async_turn_on(self, **kwargs):
        """Turn the light on."""
        if await self.try_command(self.on):
            self._state = True

    async def async_turn_off(self, **kwargs):
        """Turn the light off."""
        if await self.try_command(self.off):
            self._state = False

    async def async_update(self):
        """Fetch state from the device."""
        self._state = await self.try_command(self.status)

    async def try_command(self, func):
        """Call a miio device command handling error messages."""
        try:
            result = await self.hass.async_add_executor_job(func)
            _LOGGER.debug("Response received from miio device: %s", result)
            return result
        except Exception as exc:
            #import traceback
            # _LOGGER.error(traceback.format_exc())
            _LOGGER.error("Error on command: %s", exc)
            return None

    def status(self):
        return self._device.send('get_prop', 'led') == ['1']

    def on(self):
        return self._device.send('set_led', [1]) == ['ok']

    def off(self):
        return self._device.send('set_led', [0]) == ['ok']
