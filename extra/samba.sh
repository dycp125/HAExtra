
#!/bin/sh

hdparm -I /dev/sda
hdparm -B 127 /dev/sda
hdparm -S 180 /dev/sda
hdparm -I /dev/sda
hdparm -C /dev/sda
echo -e "LABEL=STORE\t/mnt/STORE\tntfs\t\tdefaults,noatime,nodiratime\t\t\t0 0" >> /etc/fstab
#reboot

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
