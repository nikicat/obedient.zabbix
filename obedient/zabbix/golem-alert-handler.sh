#!/bin/bash -e
#
# This is a Zabbix alerting script that convert alerts to Golem events.
# In case of sending failure it writes message to the log file.
# This script should be called with subject
#   {HOST.NAME}#{TRIGGER.NAME}#{STATUS}
# and body will be added as a description for an event

if [ -n "$GOLEM_ALERT_LOG" ]; then
    exec 2> >(while read line; do echo "$(date +'%d/%m/%Y:%H:%M:%S %z')  $line" >> "$GOLEM_ALERT_LOG"; done;)
fi

to="$1"
subject="$2"
body="$3"

if [ -z "$to" ] || [ -z "$subject" ] || [ -z "$body" ]; then
    echo "Usage: $0 <responsible> <object#eventtype#status> <description>" >&2
    exit 1
fi

IFS='#' read object eventtype _status <<< "$subject"

if [ "$_status" = "PROBLEM" ]; then
    status=critical
elif [ "$_status" = "OK" ]; then
    status=ok
else
    echo "Unexpected status: $_status. Should be PROBLEM or OK" >& 2
    exit 1
fi

# Submit event
curl --silent --fail --get "https://golem.yandex-team.ru/api/events/submit.sbml" \
    --data-urlencode monitor=fqdn \
    --data-urlencode "object=$object" \
    --data-urlencode "eventtype=$eventtype" \
    --data-urlencode "status=$status" \
    --data-urlencode "info=$body"
