#!/bin/bash
SCR_T_START=$(date +%s)
START=$(date -d '1 hour ago'  '+%Y-%m-%d %H:%M:%S')
STOP=$(date '+%Y-%m-%d %H:%M:%S')
FILENAME="$(date '+%Y-%m-%d-%H:%M:%S').txt"
echo $START $STOP $FILENAME
clickhouse-client -q "select toUnixTimestamp(Time),Protocol,Src_ip,Src_port,hex(Src_ip_nat),Src_port_nat,hex(Dst_ip),Dst_port from cgnat.bras where Time between '$START' and '$STOP' order by Time" > $FILENAME

echo "Filename: $FILENAME ($(cat $FILENAME | wc -l))" >> time.txt
IFS=$'\t'
cat $FILENAME | while read -a arr; do
        #echo $SRC_IP
        RAD_PARM=$(clickhouse-client -q "select User_Name, Mac_Address from cgnat.radius where Src_ip=${arr[2]} and Time between '$START' and '$STOP' order by Time DESC limit 1")
        #echo "user:${RAD_PARM:0:10} mac:${RAD_PARM:11:25}"
        #username|mac|time|proto|src_ip|src_port|src_ip_nat|src_port_nat|dst_ip|dst_port
        SRC_IP=$(printf "%X\n" ${arr[2]})
        #echo "${RAD_PARM:0:10}|${RAD_PARM:11:25}|${arr[0]}|${arr[1]}|$SRC_IP|${arr[3]}|${arr[4]}|${arr[5]}|${arr[6]}|${arr[7]}"
        echo "${RAD_PARM:0:10}|${RAD_PARM:11:25}|${arr[0]}|${arr[1]}|$SRC_IP|${arr[3]}|${arr[4]}|${arr[5]}|${arr[6]}|${arr[7]}" >> ${FILENAME}_shatel.csv.gz
        #echo ${arr[2]}>> src_ip.txt
done
#rm -rf $FILENAME
IFS=' '
SCR_T_END=$(date +%s)
SCR_T=$((SCR_T_END - SCR_T_START))
echo  $FILENAME $SCR_T >> time.txt
exit
