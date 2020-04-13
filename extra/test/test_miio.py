
from miio.device import Device

device = Device('Airer', 'fe5a1e19a1fd91ca4138646a494a6f19')
#device_info = device.info()
#device.send("set_led", [0])
#print('%s' % device_info)
ret = device.send("get_prop", [
            # "dry",
            "led",
            # "motor",
            # "drytime",
            #"airer_location",
        ])
print('%s' % ret)