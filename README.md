# CGNAT_Log

NOTE: ********* this document has not completed yet ********

To collect CGNAT logs and store them into DB.

In this project we have Radius servers for AAA and Brases as ras. Also we need some servers to collect logs and parse them into our suitable data type and human readable and store them in clickhouse database.

Our users connect to Brases and we send Bras log's to sensors called bras_sensor, each Bras has one sensor to collect Bras logs by Rysylog  and parse it's logs.

Other sensor called Radius_sensor to sniff Radius traffic and store them by tcpdump, then parse and extract some data from radius attributes and store them into radius DB called online user.

finally bras-report.sh collect data from radius.ou(online users) and bras sensor data and store them into main DB.

For doing this project faster I use pypy to run python code faster than usual.

How to config:

1- Bras_sensor:

Please configure yout Bras to send their logs by syslog format to their bras_sensor (TCP or UDP port: 514), you need to configure Rsyslog to listen to port 514.

by using cgnat.conf file and copy it to /etc/rsyslog/conf.d/ Rsyslog parse logs(in this case Cisco Nat log format) and store them into /srv/log/cgnat/year.

bras.py will open saved logs and connects to radius DB (online users table) then save final file into /root/bras/bras-report and Main DB on database server. (you can have some main DB based on your data size)

crontab runs bras.py.

2- Radius_Sensor:

sniff received radius packet by Tcpdump and store them into /root/radius/pcap.

online-users.py will parse them and store data into Radius online user table and ~/radius/parsed_file.

old pcap will move into /tmp/old-pcap.

everything schedule by crontab.

