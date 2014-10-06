<?php
// Zabbix GUI configuration file
global $DB;
$DB["TYPE"] = 'POSTGRESQL';
$DB["SERVER"]   = '${ postgres.ship.fqdn }';
$DB["PORT"] = '${ postgres.doors['postgres'].port }';
$DB["DATABASE"] = 'zabbix';
$DB["USER"] = 'postgres';
$DB["PASSWORD"] = '';
// SCHEMA is relevant only for IBM_DB2 database
$DB["SCHEMA"]   = '';
$ZBX_SERVER = '${ backend.ship.fqdn }';
$ZBX_SERVER_PORT    = '${ backend.doors['zabbix-trapper'].port }';
$ZBX_SERVER_NAME    = '';
$IMAGE_FORMAT_DEFAULT   = IMAGE_FORMAT_PNG;
?>
