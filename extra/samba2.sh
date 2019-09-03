
#!/bin/sh

hdparm -I /dev/sda
hdparm -B 127 /dev/sda
hdparm -S 180 /dev/sda
hdparm -I /dev/sda
hdparm -C /dev/sda
echo -e "LABEL=STORE\t/mnt/STORE\tntfs\t\tdefaults,noatime,nodiratime\t\t\t0 0" >> /etc/fstab
#reboot

apt install samba #samba-vfs-modules
smbpasswd -a admin

cat <<\EOF > /etc/samba/smb.conf
[global]
server string = Storage
map to guest = Bad User
min protocol = SMB2
load printers = no
veto files = /aria.task/
access based share enum = yes

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
public = no
writable = yes
valid users = admin

[Movies]
path = /mnt/STORE/Movies
public = no
writable = yes
valid users = admin

[Documents]
path = /mnt/STORE/Documents
public = no
writable = yes
valid users = admin

EOF

/etc/init.d/smbd restart
