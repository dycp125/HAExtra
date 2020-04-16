"""Support for Xiaomi MiIO Lights."""
import logging
from collections import defaultdict

from miio import Device

import voluptuous as vol
import homeassistant.helpers.config_validation as cv

from homeassistant.components.light import PLATFORM_SCHEMA
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_TOKEN
from homeassistant.components.xiaomi_miio.light import XiaomiPhilipsAbstractLight, CONF_MODEL

_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_HOST): cv.string,
        vol.Required(CONF_TOKEN): vol.All(cv.string, vol.Length(min=32, max=32)),
        vol.Optional(CONF_NAME): cv.string,
        vol.Optional(CONF_MODEL, default='mrbond.airer.m1pro'): vol.In(
            [
                'mrbang.airer.m1',
                'mrbond.airer.m1pro',
            ]
        ),
    }
)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the light from config."""
    host = config[CONF_HOST]
    token = config[CONF_TOKEN]
    name = config.get(CONF_NAME)
    model = config.get(CONF_MODEL)
    light = MrBondAirer(host, token)
    devices = [MiioMiscLight(name or host, light, model, None)]
    async_add_entities(devices, True)


class MiioMiscLight(XiaomiPhilipsAbstractLight):
    """Representation of a XiaoMi MiIO Light."""

    @property
    def supported_features(self):
        """Return the supported features."""
        return 0

class MrBondAirerStatus:
    """Container for status reports from MrBang Airer Light."""

    def __init__(self, data):
        self.data = data

    @property
    def is_on(self):
        return self.data['led'] == '1'

    @property
    def brightness(self):
        return 100 if self.is_on else 0

    def __json__(self):
        return self.data

class MrBondAirer(Device):
    """Main class representing MrBang Airer Light."""

    def status(self):
        """Retrieve properties."""
        properties = [
            # "dry",
            "led",
            # "motor",
            # "drytime",
            # "airer_location",
        ]
        values = self.send("get_prop", properties)

        return MrBondAirerStatus(defaultdict(lambda: None, zip(properties, values)))

    def on(self):
        """Power on."""
        return self.send("set_led", [1])

    def off(self):
        """Power off."""
        return self.send("set_led", [0])
