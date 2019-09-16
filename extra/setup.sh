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

# tzsleect
# cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime

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
echo "LC_ALL=en_US.UTF-8" >> /etc/default/locale

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

# Debug
hass

systemctl --system daemon-reload
systemctl enable homeassistant
#systemctl start homeassistant


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
