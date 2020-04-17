import logging

from homeassistant.components.fan import (
    SUPPORT_SET_SPEED,
    SPEED_OFF,
    SUPPORT_OSCILLATE
)

from .fan import XiaomiGenericDevice, FEATURE_SET_CHILD_LOCK

_LOGGER = logging.getLogger(__name__)


from miio import Device

class VioMiWasher(Device):
    """Main class representing the VioMi Washer."""

    def status(self):
        """Retrieve properties."""
        properties = [
            "program",
            "wash_process",
            "wash_status",
            # "water_temp",
            # "rinse_status",
            # "spin_level",
            # "remain_time",
            # "appoint_time",
            # "be_status",
            # "run_status",
            "DryMode",
            # "child_lock"
        ]
        data = {}
        for prop in properties:
            value = self.send("get_prop", [prop])
            data[prop] = value[0] if len(value) else None
        self._program = data['program']
        return data

    def on(self):
        try:
            _LOGGER.debug("set_wash_action on")
            return self.send("set_wash_action", [1])
        except:
            _LOGGER.debug("Try to turn on")
            try:
                set_program(self._program)
            except:
                set_program('goldenwash')
            return self.send("set_wash_action", [1])

    def off(self):
        _LOGGER.debug("set_wash_action off")
        return self.send("set_wash_action", [2])

    def set_program(self, program):
        _LOGGER.debug("set_wash_program=%s", program)
        return self.send("set_wash_program", [program])

    def set_dry_mode(self, dry_mode):
        dry_mode = 17922 if dry_mode == True else int(dry_mode)
        _LOGGER.debug("SetDryMode=%s", dry_mode)
        return self.send("SetDryMode", [dry_mode])


WASH_PROGRAMS = {
    'goldenwash': '黄金洗',
    'quick': '快洗',
    'super_quick': '超快洗',
    'spin': '单脱水',
    'rinse_spin': '漂+脱',

    'dry': '黄金烘',
    'weak_dry': '低温烘',

    'refresh': '空气洗',
    'antibacterial': '除菌洗',

    'wool': '羊毛',
    'down': '羽绒服',
    'cottons': '棉织物',
    'shirt': '衬衣',
    'jeans': '牛仔',
    'underwears': '内衣',

    'drumclean': '筒清洁',
 }


class VioMiWasherEntity(XiaomiGenericDevice):
    """Representation of a Xiaomi Pedestal Fan."""

    def __init__(self, name, device, model, unique_id, retries):
        """Initialize the fan entity."""
        super().__init__(name, device, model, unique_id, retries)

        self._device_features = FEATURE_SET_CHILD_LOCK
        self._speed = None
        self._oscillate = None

    @property
    def supported_features(self):
        """Supported features."""
        return SUPPORT_SET_SPEED | SUPPORT_OSCILLATE

    async def async_update(self):
        """Fetch state from the device."""
        from miio import DeviceException

        # On state change the device doesn't provide the new state immediately.
        if self._skip_update:
            self._skip_update = False
            return

        try:
            props = await self.hass.async_add_job(self._device.status)
            _LOGGER.debug("Got new state: %s", props)

            wash_status = props["wash_status"]
            wash_process = props["wash_process"]

            self._available = True
            self._oscillate = props["DryMode"] != 0
            self._state = wash_process > 0 and wash_process < 7 and wash_status == 1
            self._speed = WASH_PROGRAMS.get(props["program"])
            self._state_attrs = props
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
    def speed_list(self):
        """Get the list of available speeds."""
        return list(WASH_PROGRAMS.values())

    @property
    def speed(self):
        """Return the current speed."""
        return self._speed

    async def async_set_speed(self, speed):
        """Set the speed of the fan."""

        _LOGGER.debug("Setting the fan speed to: %s", speed)

        if speed in [SPEED_OFF, 0]:
            await self.async_turn_off()
            return

        if speed not in WASH_PROGRAMS:
            for program in WASH_PROGRAMS:
                if speed == WASH_PROGRAMS[program]:
                    speed = program
                    break;

        await self._try_command(
            "Setting fan speed of the miio device failed.",
            self._device.set_program, speed,
        )

    @property
    def oscillating(self):
        """Return the oscillation state."""
        return self._oscillate

    async def async_oscillate(self, oscillating):
        """Set oscillation."""
        await self._try_command(
            "Setting oscillate on of the miio device failed.",
            self._device.set_dry_mode, oscillating
        )


