#!/bin/bash -exv
# because www-data haven't access to volume
id
mount -oremount,rw /etc/zabbix
chmod go+rx /etc/zabbix
#mount -oremount,ro /etc/zabbix
apachectl -e debug -DFOREGROUND
