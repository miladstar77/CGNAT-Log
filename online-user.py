from  datetime import datetime
from  dpkt.pcap import Reader
from dpkt.radius import RADIUS
from dpkt.ethernet import Ethernet
from dpkt.utils import inet_to_str
from ipaddress import ip_address
from re import search
from os import listdir, replace, makedirs, path, system
import syslog

start_time = datetime.now()
scrtime = datetime.now().strftime("%Y-%m-%d-%H%M%S")
#time_report = open("/root/radius/times.txt", "a")
pcap_dir = "/root/radius/pcap/"
parsed_dir = "/root/radius/parsed-file/{}".format(scrtime)

#read_dir -> pcap_dir
def read_pcap(dir):
    pcap_files = sorted(listdir(dir))
    if not pcap_files :
        syslog.syslog("Error >> Reading Pcap : Failed")
        exit(1)
    else:
        syslog.syslog("Reading Pcap : Success")
    #create tmp for file
    tmp_dir = "/tmp/old-pcap/{}".format(scrtime)
    makedirs(tmp_dir)
    makedirs("/root/radius/parsed-file/{}".format(scrtime))
    # move to tmp folder
    if len(pcap_files) > 1 :
        for f in range(len(pcap_files[:-1])):
            replace("/root/radius/pcap/{}".format(pcap_files[f]), "{}/{}".format(tmp_dir, pcap_files[f]))
    #for file in pcap_files[:2]:
    #    replace("/root/radius/pcap/{}".format(file), "{}/{}".format(tmp_dir, file))
    #print(pcap_files, len(pcap_files))
    return tmp_dir

#get radius attr
def rad_attr(tmp, parsed_file):
    pcap_files = sorted(listdir(tmp))
    #pcap_files = sorted(listdir(tmp))
    for pcap_file in pcap_files:
        file_start_time =  datetime.now()
        pcap_reader = open("{}/{}".format(tmp, pcap_file), 'rb')
        pcap = Reader(pcap_reader)
        sum_all = 0
        sum_ip = 0
        result = open("{}/{}.csv".format(parsed_file, pcap_file[:-5]), "a")
        print(pcap_file)
        online_user = {}
        for rad_time, buf in pcap:
            #print("packet {}".format(c))
            sum_all += 1
            pcap_time = int(rad_time)
            eth = Ethernet(buf)
            ip = eth.data
            udp = ip.data
            #if udp.ulen >= 240:
            radius_pcap = RADIUS(udp.data)
            if radius_pcap.code == 4 :
                sum_ip += 1
                #print("ip len : {} udp len : {} ".format(ip.len, udp.ulen))
                #print(radius_pcap.unpack)
                # attr tuple -> (type code, data)
                for attr in radius_pcap.attrs:
                    #print(attr[1])
                    if (attr[0] == 40) and ("x01" in str(attr[1])):
                        #print(attr[1])
                        #start>1 stop>2 interim>3
                        acct_st = 1
                    elif (attr[0] == 40) and ("x02" in str(attr[1])):
                        acct_st = 2
                    elif (attr[0] == 40) and ("x03" in str(attr[1])):
                        acct_st = 3
                    elif attr[0] == 1:
                        #print("User_Name :", attr[1].decode('UTF-8'))
                        user_name =  attr[1].decode('UTF-8')
                    elif attr[0] == 8:
                        #print("Framed-IP-Address", inet_to_str(attr[1]))
                        src_ip =  ip_address(inet_to_str(attr[1]))
                    elif attr[0] == 26:
                        user_mac_1 = attr[1].decode('iso-8859-1')
                        if search("client-mac-address", attr[1].decode('iso-8859-1')):
                            user_mac = search("((?:[\da-fA-F]{2}[\s:.-]?){6})", user_mac_1).group().replace(".","")
                            #print("Mac:::::::",mac_to_str(attr[1].decode('iso-8859-1')))
                            #print("final if :: client_mac_addr ", user_mac)
                    elif attr[0] == 32:
                        #print("NAS-Identifier", attr[1].decode('UTF-8'))
                        bras =  attr[1].decode('UTF-8')
                    #print("{},{},{},{},{},{} \n".format(acct_st, pcap_time, user_name, src_ip, user_mac, bras))
                #if( acct_st == 1  or acct_st == 3 ):
                    #online_user[user_name] = [pcap_time, int(src_ip), user_mac, bras, acct_st]
                online_user[user_name] = [pcap_time, int(src_ip), user_mac, bras, acct_st]
                #result.write("{},{},{},{},{},{} \n".format(pcap_time, user_name, int(src_ip), user_mac, bras, acct_st))
                #command.execute ("insert into ou (sip, uname, mac, bras, time, acct_st) values (%d, %d, '%s', '%s', %d, %d)"%(int(src_ip), int(user_name), user_mac, bras, pcap_time, acct_st))
                #else:
                    #pass
            #break
        for uname, item in online_user.items():
            result.write("{},{},{},{},{},{} \n".format(item[0], uname, item[1], item[2], item[3], item[4]))
            #print(item[0], uname, item[1], item[2], item[3], item[4])
        file_time = datetime.now() - file_start_time
        #time_report.write("finish time  {} : {} pkts {} process {} \n".format(pcap_file, file_time, sum_all ,sum_ip))
        syslog.syslog("{}->Process-Time: {}, Pkts: {}, Processed: {} \n".format(pcap_file, file_time, sum_all ,sum_ip))
        print("number of packet  :{} & ip process : {} online user : {} ".format(sum_all, sum_ip, len(online_user)))
        result.close()
        online_user.clear()
        #break

#send to databse
def send2db(dir):
    p_files = listdir(dir)
    for file in p_files:
        print(file)
        if (system("clickhouse-client  -d radius -q 'insert into onlineuser Format CSV' < {}/{}".format(dir, file))) == 0 :
            syslog.syslog("Sending {} to radius.onlineuser : Success".format(file))
        else:
            syslog.syslog("Unable To Send  {} To DB".format(file))
        #replace("{}/{}".format(p_dir, file), "/root/radius/sent/{}".format(file))

tmp = read_pcap(pcap_dir)

rad_attr(tmp, parsed_dir)

send2db(parsed_dir)

print("total time : ", datetime.now() - start_time)
#time_report.write("Total time: {}  \n".format(datetime.now() - start_time))
syslog.syslog("Total time {} : {}  \n".format(scrtime, datetime.now() - start_time))
#time_report.close()
exit()
