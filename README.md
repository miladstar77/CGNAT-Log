# CGNAT_Log
To collect CGNAT logs and store them into DB.

In this project we have Radius servers for AAA and Brases as ras. Also we need some servers to collect logs and parse them into our suitable data type and human readable and store them in clickhouse database.

Our users connect to Brases and we send Bras log's to sensors called bras_sensor, each Bras has one sensor to collect Bras logs by Rysylog  and parse it's logs.

Other sensor called Radius_sensor to sniff Radius traffic and store them by tcpdump, then parse and extract some data from radius attributes and store them into radius DB called online user.

finally bras-report.sh collect data from radius.ou(online users) and bras sensor data and store them into main DB.

For doing this project faster I use pypy to run python code faster than usual.

