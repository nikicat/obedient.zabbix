#!/bin/bash

mkdir /var/run/zabbix
chmod go+rwx /var/run/zabbix
/usr/sbin/zabbix_server
sleep 2
strace -e none -e exit_group -p `cat /var/run/zabbix/zabbix_server.pid`
