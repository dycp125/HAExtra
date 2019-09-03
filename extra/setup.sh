#!/bin/sh

# ============================== Basic Config ==============================
# Raspberry Pi Only
#ssh pi@hassbian
# sudo passwd root
# sudo passwd --unlock root
# sudo nano /etc/ssh/sshd_config #PermitRootLogin yes
# sudo mkdir /root/.ssh
# mkdir ~/.ssh
# sudo reboot
# # Raspberry Pi Only: Rename pi->admin
# usermod -l admin pi
# groupmod -n admin pi
# mv /home/pi /home/admin
# usermod -d /home/admin admin
# passwd admin
# raspi-config # Hostname, WiFi, locales(en_US.UTF-8/zh_CN.GB18030/zh_CN.UTF-8), Timezone
##apt install python3 python3-pip

# MacOS
#ssh root@hassbian "mkdir ~/.ssh"
#scp ~/.ssh/authorized_keys root@hassbian:~/.ssh/
#scp ~/.ssh/id_rsa root@hassbian:~/.ssh/
#scp ~/.ssh/config root@hassbian:~/.ssh/

# SSH
ssh root@hassbian "mkdir ~/.ssh"
scp ~/.ssh/authorized_keys root@hassbian:~/.ssh/
scp ~/.ssh/id_rsa root@hassbian:~/.ssh/
scp ~/.ssh/config root@hassbian:~/.ssh/

ssh admin@hassbian "mkdir ~/.ssh"
scp ~/.ssh/authorized_keys admin@hassbian:~/.ssh/
scp ~/.ssh/id_rsa admin@hassbian:~/.ssh/
scp ~/.ssh/config admin@hassbian:~/.ssh/

ssh root@hassbian

#
echo "admin ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

armbian-config #Hostname, wifi,timezone, apt-source
#echo "Asia/Shanghai" > /etc/timezone && ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime

# ============================== Home Assistant ==============================
apt update && apt upgrade -y
#apt autoclean
#apt clean
#apt autoremove -y

apt install mosquitto mosquitto-clients libavahi-compat-libdnssd-dev adb

# Armbian
apt install python3-pip python3-dev libffi-dev python3-setuptools
ln -sf /usr/bin/python3 /usr/bin/python

# Speedtest
cd /usr/local/bin
wget -O speedtest https://raw.githubusercontent.com/sivel/speedtest-cli/master/speedtest.py; chmod +x speedtest; ./speedtest

# PIP 18
##python3 -m pip install --upgrade pip # Logout after install
#curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
#python3 get-pip.py --force-reinstall

# Python 3.7+
#curl https://bc.gongxinke.cn/downloads/install-python-latest | bash

# Baidu TTS
#apt install libtiff5-dev libjpeg8-dev zlib1g-dev libfreetype6-dev liblcms2-dev libwebp-dev tcl8.6-dev tk8.6-dev python-tk
#apt install libjpeg-dev zlib1g-dev

# Home Assistant
pip3 install wheel
pip3 install homeassistant

# Auto start
cat <<EOF > /etc/systemd/system/homeassistant.service
[Unit]
Description=Home Assistant
After=network-online.target

[Service]
Type=simple
User=root
ExecStart=/usr/local/bin/hass

[Install]
WantedBy=multi-user.target

EOF

systemctl --system daemon-reload
systemctl enable homeassistant
systemctl start homeassistant

# Alias
cat <<\EOF >> ~/.bashrc
alias ls='ls $LS_OPTIONS'
alias ll='ls $LS_OPTIONS -l'
alias l='ls $LS_OPTIONS -lA'
alias mqttre='systemctl stop mosquitto; sleep 2; rm -rf /var/lib/mosquitto/mosquitto.db; systemctl start mosquitto'
alias hassre='echo .>~/.homeassistant/home-assistant.log; systemctl restart homeassistant'
alias hassup='systemctl stop homeassistant; pip3 install homeassistant --upgrade; systemctl start homeassistant'
alias hasslog='tail -f ~/.homeassistant/home-assistant.log'
EOF

exit 0

# Debug
hass

# Mosquitto
#echo "allow_anonymous true" >> /etc/mosquitto/mosquitto.conf
#systemctl stop mosquitto
#sleep 2
#rm -rf /var/lib/mosquitto/mosquitto.db
#systemctl start mosquitto
#sleep 2
#mosquitto_sub -v -t '#'

# ============================== V2Ray ==============================

curl https://install.direct/go.sh | sudo bash

cat >> /etc/v2ray/config.json << "EOF"
{

}
EOF

# ============================== Disk ==============================
hdparm -I /dev/sda
hdparm -B 127 /dev/sda
hdparm -S 180 /dev/sda
hdparm -I /dev/sda
hdparm -C /dev/sda
echo -e "/dev/sda1\t/mnt/STORE\tntfs\t\tdefaults,noatime,nodiratime\t\t\t0 0" >> /etc/fstab

# ============================== Samba ==============================
apt install samba samba-vfs-modules
smbpasswd -a admin

cat <<\EOF > /etc/samba/smb.conf
[global]
server string = Storage
map to guest = Bad User
min protocol = SMB2

ea support = yes
vfs objects = catia fruit streams_xattr
fruit:aapl = yes
readdir_attr:aapl_rsize = yes
readdir_attr:aapl_finder_info = yes
readdir_attr:aapl_max_access = yes
fruit:nfs_aces = yes
fruit:copyfile= yes
fruit:metadata = netatalk
fruit:resource = file
fruit:locking = none
fruit:encoding = private
unix extensions = yes
fruit:model = MacSamba
spotlight = no
smb2 max read = 8388608
smb2 max write = 8388608
smb2 max trans = 8388608
smb2 leases = yes
aio read size = 1
aio write size = 1
kernel oplocks = no
use sendfile = yes
strict sync = yes
sync always = no
delete veto files = true
fruit:posix_rename = yes
fruit:veto_appledouble = yes
fruit:zero_file_id = yes
fruit:wipe_intentionally_left_blank_rfork = yes
fruit:delete_empty_adfiles = yes
#disable netbios = yes
#dns proxy = no
#smb ports = 445
#name resolve order = host bcast

load printers = no
min receivefile size = 16384
write cache size = 524288
getwd cache = yes
#socket options = TCP_NODELAY IPTOS_LOWDELAY
directory mask = 0755
create mask = 0644
force directory mode = 0755
force create mode = 0644
access based share enum = yes
veto files = /aria.task/

[Downloads]
path = /mnt/STORE/Downloads
public = yes
writable = yes

[Public]
path = /mnt/STORE/Public
public = yes
write list = admin

[Music]
path = /mnt/STORE/Music
public = yes
write list = admin

[Pictures]
path = /mnt/STORE/Pictures
public = yes
write list = admin

[Movies]
path = /mnt/STORE/Movies
public = yes
write list = admin

[Documents]
path = /mnt/STORE/Documents
public = no
writable = yes
valid users = admin

EOF
/etc/init.d/smbd restart

# ============================== Aria ==============================
apt install aria2c
cat <<\EOF > /etc/init.d/aria
#!/bin/sh

start()
{
  if [ ! -z "$1" ]; then
    DDIR="$1"
  elif [ -d /mnt/STORE/Downloads ]; then
    DDIR=/mnt/STORE/Downloads
  elif [ -d ~/Downloads ]; then
    DDIR=~/Downloads
  else
    DDIR=$(pwd)
  fi

  TASK=$DDIR/aria.task
  if [ ! -r $TASK ]; then touch $TASK; fi

  ARIA2C=$(cd "${0%/*}"; pwd)/aria2c
  if [ ! -x $ARIA2C ]; then ARIA2C=aria2c; fi

  XOPT="--rpc-certificate=/root/.homeassistant/fullchain.cer --rpc-private-key=/root/.homeassistant/privkey.pem --rpc-secure=true"
  $ARIA2C -D -d $DDIR -c -i $TASK --save-session=$TASK --enable-rpc --rpc-listen-all --rpc-allow-origin-all --file-allocation=falloc --disable-ipv6 $XOPT
}

case "$1" in
  start)
    echo "Starting aria2c daemon..."
    start $2
    ;;
  stop)
    echo "Shutting down aria2c daemon..."
    killall aria2c
    ;;
  restart)
    killall aria2c
    sleep 1
    start $2
    ;;
  '')
    echo "Aria2c helper by Yonsm"
    echo
    echo "Usage: $0 [start|stop|restart|<DIR>] [DIR]"
    echo
    ;;
  *)
    start $1
    ;;
esac

EOF

chmod 755 /etc/init.d/aria
#ln -s /mnt/STORE/Downloads ~
update-rc.d aria defaults

# ============================== Transmission ==============================
apt install transmission


# ============================== Deprecated Config ==============================
# Global Customization file
#homeassistant:
  #customize_glob: !include customize_glob.yaml
  # auth_providers:
  #   - type: homeassistant
  #   - type: trusted_networks
  #   - type: legacy_api_password

#http:
  #api_password: !secret http_password
  # trusted_networks:
  # - 127.0.0.1
  # - 192.168.1.0/24
  # - 192.168.2.0/24

# Enables the frontend
#frontend:
  #javascript_version: latest
  #extra_html_url:
  #  - /local/custom_ui/state-card-button.html
  # - /local/custom_ui/state-card-custom-ui.html
  #extra_html_url_es5:
  #  - /local/custom_ui/state-card-button.html
  # - /local/custom_ui/state-card-custom-ui-es5.html

# Customizer
# customizer:
#   custom_ui: local
  # customize.yaml
  # config:
  #   extra_badge:
  #     - entity_id: switch.speaker
  #       attribute: original_state
  #   entities:
  #     - entity: switch.speaker
  #       icon: mdi:video-input-component
  #       service: mqtt.publish
  #       data:
  #         topic: NodeMCU3/relay/0/set
  #         payload: toggle
  # custom_ui_state_card: state-card-button
  #dashboard_static_text_attribute: original_state

#recorder:
#  purge_keep_days: 2
#  db_url: sqlite:////tmp/home-assistant.db

#logger:
  # default: warning
  #logs:
  #homeassistant.components.homekit: debug

# Text to speech
#tts:
#  - platform: google
#    language: zh-cn
#   - platform: baidu
#     app_id: !secret baidu_app_id
#     api_key: !secret baidu_api_key
#     secret_key: !secret baidu_secret_key

#shell_command:
  #genie_power: 'adb connect Genie; adb -s Genie shell input keyevent 26'
  #genie_dashboard: 'adb connect Genie; adb -s Genie shell am start -n de.rhuber.homedash/org.wallpanelproject.android.WelcomeActivity'


# input_boolean:
#   wall_fan_state:
#   wall_fan_osc:
#   wall_fan_direction:

# input_select:
#   wall_fan_speed:
#     options: [low, medium, high]
