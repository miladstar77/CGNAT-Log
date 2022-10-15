#!/bin/bash
#set -xu
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin
DIR="/root/cgnat/report/"
SCR_T_START=$(date +%s)
START=$(date -d '20 minute  ago'  '+%Y-%m-%d %H:%M:00')
STOP=$(date -d '16  minute ago' '+%Y-%m-%d %H:%M:59')
FILE=$(echo $(date -d "20 minutes ago" +"%Y%m%d%H%M")_3_shatel.csv)
FTP_DIR=$(echo ${FILE:0:8})
#echo $FILE $START $STOP

clickhouse-client -d cgnat -q "select uname, mac, toUnixTimestamp(time),proto,hex(sip),sport,hex(nip),nport,hex(dip),dport from nat where time between '$START' and '$STOP' order by time " | tr '\t' '|' > $DIR$FILE
gzip $DIR$FILE
FILE="$FILE.gz"
#upload report to FTP server
curl -T $DIR$FILE ftp://ftp-server-ip/$FTP_DIR/ --ftp-create-dirs --user "user:pass"
SCR_T_END=$(date +%s)
logger -t extract.sh "$START -> $STOP ScrTime: $((SCR_T_END - SCR_T_START)) $FILE  Saved To $DIR"
exit 0
