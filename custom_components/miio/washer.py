"""
Support for Xiaomi Mi Smart Pedestal Fan.

For more details about this platform, please refer to the documentation
https://home-assistant.io/components/fan.xiaomi_miio/
"""
import asyncio
import logging

from homeassistant.components.fan import (
    SUPPORT_SET_SPEED,
    DOMAIN,
    SPEED_OFF,
    SUPPORT_OSCILLATE,
    SUPPORT_DIRECTION,
    ATTR_SPEED,
    ATTR_SPEED_LIST,
    ATTR_OSCILLATING,
    ATTR_DIRECTION,
)
from homeassistant.const import CONF_NAME, CONF_HOST, CONF_TOKEN, ATTR_ENTITY_ID

_LOGGER = logging.getLogger(__name__)

AVAILABLE_ATTRIBUTES_FAN = {
    "program": "program",
    "wash_process": "wash_process",
    "wash_status": "wash_status",
    "water_temp": "water_temp",
    "rinse_status": "rinse_status",
    "spin_level": "spin_level",
    "remain_time": "remain_time",
    "appoint_time": "appoint_time",
    "be_status": "be_status",
    "run_status": "run_status",
    "DryMode": "DryMode",
    "child_lock": "child_lock",
}

FAN_SPEED_LEVEL1 = "goldenwash"
FAN_SPEED_LEVEL2 = "spin"

FAN_SPEED_LIST = {
    SPEED_OFF: range(0, 1),
    FAN_SPEED_LEVEL1: range(1, 26),
    FAN_SPEED_LEVEL2: range(26, 51),
}

FAN_SPEED_VALUES = {
    SPEED_OFF: 0,
    FAN_SPEED_LEVEL1: 1,
    FAN_SPEED_LEVEL2: 35,
}

from miio import Fan

class VioMiWasher(Fan):
    """Representation of a XiaoMi MiIO Light."""

from .fan import XiaomiGenericDevice, FEATURE_SET_CHILD_LOCK

class VioMiWasherEntity(XiaomiGenericDevice):
    """Representation of a Xiaomi Pedestal Fan."""

    def __init__(self, name, device, model, unique_id, retries):
        """Initialize the fan entity."""
        super().__init__(name, device, model, unique_id, retries)

        self._device_features = FEATURE_SET_CHILD_LOCK
        self._available_attributes = AVAILABLE_ATTRIBUTES_FAN
        self._speed_list = list(FAN_SPEED_LIST)
        self._speed = None
        self._oscillate = None
        self._natural_mode = False

        self._state_attrs[ATTR_SPEED] = None
        self._state_attrs.update(
            {attribute: None for attribute in self._available_attributes}
        )

    @property
    def supported_features(self) -> int:
        """Supported features."""
        return SUPPORT_SET_SPEED | SUPPORT_OSCILLATE | SUPPORT_DIRECTION

    async def async_update(self):
        """Fetch state from the device."""
        from miio import DeviceException

        # On state change the device doesn't provide the new state immediately.
        if self._skip_update:
            self._skip_update = False
            return

        try:
            state = await self.hass.async_add_job(self._device.status)
            _LOGGER.debug("Got new state: %s", state)

            self._available = True
            self._oscillate = state.oscillate
            self._natural_mode = state.natural_speed != 0
            self._state = state.is_on

            if self._natural_mode:
                for level, range in FAN_SPEED_LIST.items():
                    if state.natural_speed in range:
                        self._speed = level
                        self._state_attrs[ATTR_SPEED] = level
                        break
            else:
                for level, range in FAN_SPEED_LIST.items():
                    if state.direct_speed in range:
                        self._speed = level
                        self._state_attrs[ATTR_SPEED] = level
                        break

            self._state_attrs.update(
                {
                    key: self._extract_value_from_attribute(state, value)
                    for key, value in self._available_attributes.items()
                }
            )
            self._retry = 0

        except DeviceException as ex:
            self._retry = self._retry + 1
            if self._retry < self._retries:
                _LOGGER.info(
                    "Got exception while fetching the state: %s , _retry=%s",
                    ex,
                    self._retry,
                )
            else:
                self._available = False
                _LOGGER.error(
                    "Got exception while fetching the state: %s , _retry=%s",
                    ex,
                    self._retry,
                )

    @property
    def speed_list(self) -> list:
        """Get the list of available speeds."""
        return self._speed_list

    @property
    def speed(self):
        """Return the current speed."""
        return self._speed

    async def async_set_speed(self, speed: str) -> None:
        """Set the speed of the fan."""
        if self.supported_features & SUPPORT_SET_SPEED == 0:
            return

        _LOGGER.debug("Setting the fan speed to: %s", speed)

        if speed.isdigit():
            speed = int(speed)

        if speed in [SPEED_OFF, 0]:
            await self.async_turn_off()
            return

        # Map speed level to speed
        if speed in FAN_SPEED_VALUES:
            speed = FAN_SPEED_VALUES[speed]

        if self._natural_mode:
            await self._try_command(
                "Setting fan speed of the miio device failed.",
                self._device.set_natural_speed,
                speed,
            )
        else:
            await self._try_command(
                "Setting fan speed of the miio device failed.",
                self._device.set_direct_speed,
                speed,
            )

    async def async_set_direction(self, direction: str) -> None:
        """Set the direction of the fan."""
        from miio.fan import MoveDirection

        if direction in ["left", "right"]:
            if self._oscillate:
                await self._try_command(
                    "Setting oscillate off of the miio device failed.",
                    self._device.set_oscillate,
                    False,
                )

            await self._try_command(
                "Setting move direction of the miio device failed.",
                self._device.set_rotate,
                MoveDirection(direction),
            )

    @property
    def oscillating(self):
        """Return the oscillation state."""
        return self._oscillate

    async def async_oscillate(self, oscillating: bool) -> None:
        """Set oscillation."""
        if oscillating:
            await self._try_command(
                "Setting oscillate on of the miio device failed.",
                self._device.set_oscillate,
                True,
            )
        else:
            await self._try_command(
                "Setting oscillate off of the miio device failed.",
                self._device.set_oscillate,
                False,
            )

    async def async_set_oscillation_angle(self, angle: int) -> None:
        """Set oscillation angle."""
        if self._device_features & FEATURE_SET_OSCILLATION_ANGLE == 0:
            return

        await self._try_command(
            "Setting angle of the miio device failed.", self._device.set_angle, angle
        )

    async def async_set_led_brightness(self, brightness: int = 2):
        """Set the led brightness."""
        if self._device_features & FEATURE_SET_LED_BRIGHTNESS == 0:
            return

        from miio.fan import LedBrightness

        await self._try_command(
            "Setting the led brightness of the miio device failed.",
            self._device.set_led_brightness,
            LedBrightness(brightness),
        )

    async def async_set_natural_mode_on(self):
        """Turn the natural mode on."""
        if self._device_features & FEATURE_SET_NATURAL_MODE == 0:
            return

        self._natural_mode = True
        await self.async_set_speed(self._speed)

    async def async_set_natural_mode_off(self):
        """Turn the natural mode off."""
        if self._device_features & FEATURE_SET_NATURAL_MODE == 0:
            return

        self._natural_mode = False
        await self.async_set_speed(self._speed)

