import logging
import datetime

from miio import Device
from .fan import XiaomiGenericDevice, FEATURE_SET_CHILD_LOCK

_LOGGER = logging.getLogger(__name__)

WASH_MODES = ['立即洗', '立即洗烘', '预约洗', '预约洗烘']

class VioMiEntity(XiaomiGenericDevice):
    """Representation of a Xiaomi Pedestal Fan."""

    @property
    def icon(self):
        """Return the icon to use for device if any."""
        return 'mdi:washing-machine'

    @property
    def speed_list(self):
        """Get the list of available speeds."""
        return WASH_MODES

    @property
    def speed(self):
        """Return the current speed."""
        return self._device.mode

    async def async_update(self):
        """Fetch state from the device."""

        # On state change the device doesn't provide the new state immediately.
        if self._skip_update:
            self._skip_update = False
            return

        try:
            attrs = await self.hass.async_add_job(self._device.status)
            _LOGGER.debug("Got new state: %s", attrs)

            self._available = True
            self._retry = 0
            self._state_attrs = attrs

            wash_status = attrs["wash_status"]
            wash_process = attrs["wash_process"]
            self._state = wash_process > 0 and wash_process < 7 and wash_status == 1
            
            program = attrs["program"]
            dry_mode = program == 'dry' or program == 'weak_dry' or attrs["DryMode"] != 0
            appoint_time = attrs["appoint_time"]
            self._device.mode = ('预约' if appoint_time else '立即') + ('洗烘' if dry_mode else '洗')

        except Exception as ex:
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

    async def async_set_speed(self, speed):
        """Set the speed of the fan."""
        _LOGGER.debug("Setting the fan speed to: %s", speed)
        await self._try_command(
            "Setting fan speed of the miio device failed.",
            self._device.set_mode, speed,
        )
        #self._device.mode = speed

    async def async_turn_on(self, speed, **kwargs):
        if speed:
            await self.async_set_speed(speed)
        else:
            await super().async_turn_on()


class VioMiWasher(Device):
    """Main class representing the VioMi Washer."""
    def __init__(self, host, token):
        super().__init__(host, token)
        self.mode = WASH_MODES[0]

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
            "appoint_time",
            # "be_status",
            # "run_status",
            "DryMode",
            # "child_lock"
        ]
        data = {}
        try:
            for prop in properties:
                value = self.send("get_prop", [prop])
                data[prop] = value[0] if len(value) else None
            data['dash_extra_forced'] = True
        except Exception as ex:
            _LOGGER.debug("Exception on status: %s. Trying to turn on...", ex)
            self.up()

        return data

    def on(self):
        _LOGGER.debug("Turn washer ON!")
        self.set_mode() # We should set mode to ensure appoint time
        return self.send("set_wash_action", [1])

    def off(self):
        _LOGGER.debug("Turn washer OFF!")
        return self.send("set_wash_action", [2])

    def up(self):
        return self.send("set_wash_program", ['goldenwash'])

    def set_mode(self, mode=None):
        if mode is not None:
            self.mode = mode if mode in WASH_MODES else WASH_MODES[0]

        dry_mode = '33282' if self.mode.endswith('烘') else '0'

        if self.mode.startswith('预约'):
            now = datetime.datetime.now()
            hour = now.hour
            if now.minute > 10:
                hour += 1
            if hour <= 5:
                appoint_time = 8 - hour
            elif hour >= 13:
                appoint_time = 8 + 24 - hour
            else:
                appoint_time = 0
        else:
            appoint_time = 0

        _LOGGER.debug('set_mode: dry_mode=%s, appoint_time=%s', dry_mode, appoint_time)

        self.up()
        self.send("SetDryMode", [dry_mode])
        return self.send("set_appoint_time", [appoint_time])
