import logging
import time
import datetime

from miio import Device
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_TOKEN
from homeassistant.components.fan import FanEntity, SUPPORT_SET_SPEED, SUPPORT_OSCILLATE, SUPPORT_DIRECTION, PLATFORM_SCHEMA

_LOGGER = logging.getLogger(__name__)


APPOINT_MIN = 1  # 3
APPOINT_MAX = 23  # 19
APPOINT_CLOCK = 8
WASH_MODES = ['立即洗衣', '立即洗烘', '预约洗衣', '预约洗烘']
DEFAULT_WASH_MODE = '预约洗衣'

WASH_PROGRAMS = {
    'goldenwash': '黄金洗',
    'quick': '快洗',
    'super_quick': '超快洗',

    'antibacterial': '除菌洗',
    'refresh': '空气洗',

    'dry': '黄金烘',
    'weak_dry': '低温烘',

    'rinse_spin': '漂+脱',
    'spin': '单脱水',
    'drumclean': '筒清洁',

    'cottons': '棉织物',
    'down': '羽绒服',
    'wool': '羊毛',
    'shirt': '衬衣',
    'jeans': '牛仔',
    'underwears': '内衣',
}

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_HOST): cv.string,
        vol.Required(CONF_TOKEN): vol.All(cv.string, vol.Length(min=32, max=32)),
        vol.Optional(CONF_NAME): cv.string,
    }
)


def setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the light from config."""
    host = config[CONF_HOST]
    token = config[CONF_TOKEN]
    name = config.get(CONF_NAME)
    async_add_entities([VioMiWasher(name, host, token)], True)


class VioMiDevice(Device):

    def update(self, status):
        """Retrieve properties."""
        props = [
            "program",
            "wash_process",
            "wash_status",
            # "water_temp",
            # "rinse_status",
            # "spin_level",
            "remain_time",
            "appoint_time",
            # "be_status",
            # "run_status",
            "DryMode",
            # "child_lock"
        ]

        try:
            for prop in props:
                status[prop] = self.send('get_prop', [prop])[0]
        except Exception as exc:
            _LOGGER.error("Error on update: %s", exc)
            return None

        return status['wash_status'] == 1 and ((status['wash_process'] > 0 and status['wash_process'] < 7) or status['appoint_time'])

    def control(self, name, value):
        _LOGGER.debug('Waher control: %s=%s', name, value)
        try:
            return self.send(name, [value]) == ['ok']
        except Exception as exc:
            _LOGGER.error("Error on control: %s", exc)
            return None


class VioMiWasher(FanEntity):
    def __init__(self, name, host, token):
        self._name = name or host
        self._device = VioMiDevice(host, token)
        self._status = {'dash_extra_forced': True, 'genie_deviceType': 'washmachine'}
        self._state = None
        self._skip_update = False
        self._dry_mode = 0
        self._appoint_time = 0

    @property
    def supported_features(self):
        """Flag supported features."""
        return SUPPORT_SET_SPEED | SUPPORT_OSCILLATE | SUPPORT_DIRECTION

    @property
    def name(self):
        """Return the name of the device if any."""
        return self._name

    @property
    def icon(self):
        """Return the icon to use for device if any."""
        return 'mdi:washing-machine'

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

        self._state = self._device.update(self._status)
        if self._state: # Update dash name for status
            dash_name = '剩' + str(self._status['remain_time']) + '分'
            appoint_time = self._status['appoint_time']
            if appoint_time:
                dash_name += '/' + str(appoint_time) + '时'
            if self._status['DryMode']:
                dash_name += '+烘'
            self._status['dash_name'] = dash_name
        elif 'dash_name' in self._status:
            del self._status['dash_name']

    @property
    def is_on(self):
        """Return true if device is on."""
        return self._state == True

    def turn_on(self, speed=None, **kwargs):
        """Turn the device on."""
        _LOGGER.debug('turn_on: speed=%s, kwargs=%s', speed, kwargs)

        if speed:
            self.set_speed(speed)
        else:
            self._device.control('set_wash_program', self._status.get('program') or 'goldenwash')
        time.sleep(1)

        if self._status.get('DryMode') != dry_mode:
            if not self._device.control("SetDryMode", dry_mode):
                return
            time.sleep(1)

        if appoint_time < 0:
            appoint_clock = -appoint_time
            now = datetime.datetime.now()
            hour = now.hour
            if now.minute > 10:
                hour += 1
            if hour <= appoint_clock - APPOINT_MIN:
                appoint_time = appoint_clock - hour
            elif hour >= appoint_clock + 24 - APPOINT_MAX:
                appoint_time = appoint_clock + 24 - hour
            else:
                appoint_time = 0

        if self._device.control('set_appoint_time' if appoint_time else 'set_wash_action', appoint_time or 1):
            self._state = True
            self._skip_update = True

    def turn_off(self, **kwargs):
        """Turn the device off."""
        if self._device.control('set_wash_action', 2):
            self._state = False
            self._skip_update = True

    @property
    def speed_list(self):
        """Get the list of available speeds."""
        return list(WASH_PROGRAMS.values())

    @property
    def speed(self):
        """Return the current speed."""
        return WASH_PROGRAMS.get(self._status.get('program'))

    def set_speed(self, speed):
        """Set the speed of the fan."""
        _LOGGER.debug('set_speed: speed=%s', speed)
        if speed == None or speed == 'off':
            return self.turn_off()

        for program in WASH_PROGRAMS:
            if WASH_PROGRAMS[program] == speed:
                if self._device.control('set_wash_program', program):
                    self._status['program'] = program
                    self._skip_update = True
                return

        for control in speed.split(','):
            params = control.split('=')
            if len(params) == 2:
                if not self._device.control(params[0], params[1]):
                    return

    @property
    def oscillating(self):
        """Return the oscillation state."""
        return bool(self._dry_mode)

    def oscillate(self, oscillating):
        """Oscillate the fan."""
        self._dry_mode = int(oscillating)
        if self._dry_mode == 1:
            self._dry_mode = 30721
        _LOGGER.debug("oscillate: dry_mode=%s", self._dry_mode)

    @property
    def current_direction(self):
        """Return the current direction of the fan."""
        return 'reverse' if self._appoint_time else 'forward'

    def set_direction(self, direction):
        """Set the direction of the fan."""
        self._appoint_time = direction if type(direction) is int else (-8 if direction == 'reverse' or direction == True else 0)
        _LOGGER.debug("set_direction: appoint_time=%s", self._appoint_time)

