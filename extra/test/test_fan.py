#!/usr/bin/env python3

from miio.device import Device

device = Device('192.168.1.28', '6dd1ec1c895a61d1b994b4a6242efe56')
#device.send("set_wash_program", ['goldenwash'])
device_info = device.info()
print('%s' % device_info)

#device.send("set_wash_action", [0]) # 0=Pause/1=Wash/2=PowerOff
#device.send("SetDryMode", ['17922']) # 0
#device.send("set_appoint_time", ['5']) # 0

properties = [
    # "angle",
    # "speed",
    # "poweroff_time",
    "power",
    # "ac_power",
    # "angle_enable",
    # "speed_level",
    # "natural_level",
    # "child_lock",
    # "buzzer",
    # "led_b",
    # "use_time",
        ]

# Limited to a single property per request
values = []
for prop in properties:
    values.extend(device.send("get_prop", [prop]))

print('%s' % values)
exit()

