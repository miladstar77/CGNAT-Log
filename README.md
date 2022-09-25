# CGNAT_Log
to collect CGNAT logs and store them into DB
In this project we have Radius servers for AAA and Brases as ras.
Our users connect to Brases and we send Bras log's to sensors called bras_sensor, each Bras has one sensor to collect and parse it's logs.
Other sensor called Radius_sensor to sniff Radius traffic and store them by tcpdump, then parse extract some data from radius attributes and store them into radius DB called online user.
finally bras-report.sh collect data from radius.ou(online users) and bras sensor data and store them into main DB.
