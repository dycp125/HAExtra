import logging
import datetime

from miio import Device
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_TOKEN
from homeassistant.components.fan import FanEntity, SUPPORT_SET_SPEED, PLATFORM_SCHEMA

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


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the light from config."""
    host = config[CONF_HOST]
    token = config[CONF_TOKEN]
    name = config.get(CONF_NAME)
    async_add_entities([VioMiWasher(name, host, token)], True)


class VioMiWasher(FanEntity):
    def __init__(self, name, host, token):
        self._name = name or host
        self._device = Device(host, token)
        self._attrs = None
        self._state = False
        self._mode = DEFAULT_WASH_MODE
        self._skip_update = False

    @property
    def supported_features(self):
        """Flag supported features."""
        return SUPPORT_SET_SPEED

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
        return self._attrs is not None

    @property
    def device_state_attributes(self):
        """Return the state attributes of the device."""
        return self._attrs

    @property
    def speed_list(self):
        """Get the list of available speeds."""
        return WASH_MODES

    @property
    def speed(self):
        """Return the current speed."""
        return self._mode

    @property
    def is_on(self):
        """Return true if device is on."""
        return self._state

    async def async_update(self):
        """Fetch state from the device."""
        if self._skip_update:
            self._skip_update = False
            return

        attrs = await self.try_command(self.status)
        self._state = attrs is not None and attrs['wash_status'] == 1 and (
            (attrs['wash_process'] > 0 and attrs['wash_process'] < 7) or attrs['appoint_time'])
        self._attrs = attrs
        # if self._state: # 仅做开启状态时获取模式
        #     program = attrs['program']
        #     dry_mode = program == 'dry' or program == 'weak_dry' or attrs['DryMode'] != 0
        #     self._mode = ('预约' if attrs['appoint_time'] else '立即') + ('洗烘' if dry_mode else '洗衣')

    async def async_turn_on(self, speed=None, **kwargs):
        """Turn the device on."""
        if speed:
            await self.async_set_speed(speed)
            return
        result = await self.try_command(self.on)
        if result:
            self._state = True
            self._skip_update = True

    async def async_turn_off(self, **kwargs):
        """Turn the device off."""
        result = await self.try_command(self.off)
        if result:
            self._state = False
            self._skip_update = True

    async def async_set_speed(self, speed):
        """Set the speed of the fan."""
        _LOGGER.debug("Setting washer mode to: %s", speed)
        self._mode = speed  # if speed in WASH_MODES else DEFAULT_WASH_MODE

    async def try_command(self, func):
        """Call a miio device command handling error messages."""
        try:
            result = await self.hass.async_add_job(func)
            _LOGGER.debug("Response received from miio device: %s", result)
            return result
        except Exception as exc:
            #import traceback
            # _LOGGER.error(traceback.format_exc())
            _LOGGER.error("Error on command: %s", exc)
            return None

    def status(self):
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
        attrs = {'dash_extra_forced': True, 'genie_deviceType': 'washmachine'}
        for prop in props:
            value = self._device.send("get_prop", [prop])
            attrs[prop] = value[0] if len(value) else None

        dash_name = WASH_PROGRAMS[attrs['program']]
        if attrs['DryMode']:
            dash_name += '+烘'
        remain_time = attrs['remain_time']
        if remain_time:
            dash_name += ' ' + str(remain_time)
        appoint_time = attrs['appoint_time']
        if appoint_time:
            dash_name += '/' + str(appoint_time)
        attrs['dash_name'] = dash_name

        return attrs

    def on(self):
        # if self._attrs['program'] != 'goldenwash' or self._attrs['wash_process'] == 7:
        self.send("set_wash_program", 'goldenwash')

        dry_mode = 30721 if self._mode.endswith('烘') else 0
        if self._attrs['DryMode'] != dry_mode:
            self.send("SetDryMode", dry_mode)

        if self._mode.startswith('预约'):
            now = datetime.datetime.now()
            hour = now.hour
            if now.minute > 10:
                hour += 1
            if hour <= APPOINT_CLOCK - APPOINT_MIN:
                appoint_time = APPOINT_CLOCK - hour
            elif hour >= APPOINT_CLOCK + 24 - APPOINT_MAX:
                appoint_time = APPOINT_CLOCK + 24 - hour
            else:
                appoint_time = 0
        else:
            appoint_time = 0

        if appoint_time:
            result = self.send("set_appoint_time", appoint_time)
        else:
            result = self.send("set_wash_action", 1)
        return result == ['ok']

    def off(self):
        return self.send('set_wash_action', 2) == ['ok']

    def send(self, command, param):
        _LOGGER.debug('Send command: %s=%s', command, param)
        return self._device.send(command, [param])
