# CGNAT_Log

NOTE: ********* this document has not completed yet ********

To collect CGNAT logs and store them in DB.

In this project Radius servers for AAA and Brases as ras. Also, we need some servers to collect logs and parse them into our appropriate data type, human-readable and store them in the clickhouse database.

Our users connect to Brases and we send Bras log's to sensors called bras_sensor, each Bras has one sensor to collect Bras logs by Rsyslog  and parse its logs.

Another sensor called Radius_sensor sniffs Radius traffic and store them by Tcpdump, then parse and extracts some data from radius attributes and stores them into radius DB called online user.

finally bras-report.sh collect data from radius.ou(online users) and bras sensor data and store them in the main DB.

For doing this project faster I use PyPy to run python code faster than usual.

How to config:

1- Bras_sensor:

Please configure Bras to send logs by Syslog format to bras_sensor (TCP or UDP port: 514), you need to configure Rsyslog to listen to port 514.

by using cgnat.conf file and copy it to /etc/rsyslog/conf.d/ Rsyslog parse logs(in this case Cisco Nat log format) and store them into /srv/log/cgnat/year.

bras.py will open saved logs and connects to radius DB (online users table) then save final file into /root/bras/bras-report and Main DB on database server. (you can have some main DB based on your data size)

crontab runs bras.py.

2- Radius_Sensor:

sniff received radius packets by Tcpdump and store them into /root/radius/pcap.

online-users.py will parse them and store data in Radius online user table and ~/radius/parsed_file.

old pcap will move into /tmp/old-pcap.

everything is scheduled by crontab.
