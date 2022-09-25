#!/bin/bash
SCR_T_START=$(date +%s)
START=$(date -d '10 minute  ago'  '+%Y-%m-%d %H:%M:00')
STOP=$(date -d '10 minute ago' '+%Y-%m-%d %H:%M:59')
FILENAME=$(echo $(date -d "10 minutes ago" +"%Y%m%d%H%M")_shatel.csv.gz)
echo $FILENAME $START $STOP
clickhouse-client -d cgnat -q "select uname, mac, toUnixTimestamp(time),proto,hex(sip),sport,hex(nip),nport,hex(dip),dport from nat where time between '$START' and '$STOP' order by time " | tr '\t' '|' > /root/cgnat-report/final-report/$FILENAME
SCR_T_END=$(date +%s)
SCR_T=$((SCR_T_END - SCR_T_START))
exit
