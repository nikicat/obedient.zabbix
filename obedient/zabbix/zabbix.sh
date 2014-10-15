#!/bin/bash -exv

# Apply shared memory settings
sysctl kernel.shmall=$((16 * 1024**3 / 4096))  # total shared memory size in pages
sysctl kernel.shmmax=$((2 * 1024**3))  # max shared memory segment size in bytes

mkdir /var/run/zabbix
chmod go+rwx /var/run/zabbix
/usr/sbin/zabbix_server
sleep 2
# Track server exit
strace -e none -e exit_group -p `cat /var/run/zabbix_server.pid`
