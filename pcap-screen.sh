#!/bin/bash
set -u
screen -S Never-close-screen -d -m tcpdump -i ens224  udp dst port '1812 or 1814 or 1815' -G 60 -w /root/radius/pcap/pcap-%F-%T.pcap
