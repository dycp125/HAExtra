"""Support for ASUSWRT devices."""
import logging

from miio import Device

import voluptuous as vol
import homeassistant.helpers.config_validation as cv

from homeassistant.const import CONF_HOST, CONF_TOKEN, CONF_NAME
from homeassistant.helpers.discovery import async_load_platform

_LOGGER = logging.getLogger(__name__)

DOMAIN = "mrbond_airer"

AIRER_PROPS = [
            "dry",
            "led",
            "motor",
            # "drytime",
            # "airer_location",
]

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_HOST): cv.string,
                vol.Required(CONF_TOKEN): vol.All(cv.string, vol.Length(min=32, max=32)),
                vol.Optional(CONF_NAME): cv.string,
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)


async def async_setup(hass, config, retry_delay=FIRST_RETRY_TIME):
    """Set up the asuswrt component."""

    conf = config[DOMAIN]
    host = conf[CONF_HOST]
    token = conf[CONF_TOKEN]
    name = conf.get(CONF_NAME) or host
    hass.data[DOMAIN] = MiioDevice(host, token)

    hass.async_create_task(async_load_platform(hass, "light", DOMAIN, name, config))
    hass.async_create_task(async_load_platform(hass, "cover", DOMAIN, name + '灯', config))

    return True


class MiioDevice(Device):
    """Representation of MrBond Airer Light."""

    def __init__(self, host, token):
        """Initialize the light device."""
        super().__init__(host, token)
        self.status = {}
        self.available = False

    def update(self):
        """Fetch state from the device."""
        try:
            for prop in AIRER_PROPS:
                self.status[prop] = self.send('get_prop', [prop])[0]
            self.available = True
        except Exception as exc:
            _LOGGER.error("Error on update: %s", exc)
            self.available = False

    def control(self, name, value):
        try:
            result = self.send(name, [value])
            _LOGGER.debug("Response from miio control: %s", result)
            return result == ['ok']
        except Exception as exc:
            #import traceback
            # _LOGGER.error(traceback.format_exc())
            _LOGGER.error("Error on miio control: %s", exc)
            #self.available = False
            return None

class MiioEntity():
    """Representation of MrBond Airer Light."""

    def __init__(self, hass, name, device):
        """Initialize the light device."""
        self._hass = hass
        self._name = name
        self._device = device

    @property
    def name(self):
        """Return the name of the device if any."""
        return self._name

    @property
    def available(self):
        """Return true when state is known."""
        return self._device.available

    @property
    def device_state_attributes(self):
        """Return the state attributes of the device."""
        return self._device.status
