
from miio.device import Device

device = Device('Washer', '1f63e0afaa20d062223b24c98eca7c11')
device_info = device.info()
print('%s' % device_info)

ret = device.send("get_prop", [
    #"program",
    "wash_process",
    #"wash_status","water_temp","rinse_status","spin_level","remain_time","appoint_time","be_status","run_status","DryMode","child_lock"
    ])
print('%s' % ret)
exit()
device.send("set_wash_program", ['goldenwash'])
device.send("set_wash_action", [0])
exit()

device = Device('Airer', 'fe5a1e19a1fd91ca4138646a494a6f19')
#device_info = device.info()
#device.send("set_led", [0])
#print('%s' % device_info)
ret = device.send("get_prop", [
            "dry",
            "led",
            "motor",
            "drytime",
            "airer_location",
        ])
print('%s' % ret)