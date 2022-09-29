from datetime import datetime, timedelta
from os import listdir, system, replace, makedirs, remove, path
import csv
import brashostname
import syslog

#script running  time calculate
execute_t1 = datetime.now()
# script running time
scrtime = datetime.now().strftime("%m%d%H%M%S")
year = datetime.now().strftime("%Y")
#bras name of sniffer
bras_name = brashostname.bras_name
#print(bras_name)
syslog.syslog("{}".format(bras_name))
#dir
rsyslog_dir = "/srv/log/cgnat/{}".format(year)
rsyslog_backup = "/srv/log/cgnat/sent/{}/{}".format(year, scrtime)
rad_files = "/root/bras/radius-files"
bras_report = "/root/bras/bras-report"

#read rsyslog logs
def rsyslog_logs(rsyslog_dir):
    rsyslog_files = sorted(listdir(rsyslog_dir))
    if not rsyslog_files :
        syslog.syslog("Error Reading Rsyslog Logs: Failed >> There Is No File In {}".format(rsyslog_dir))
        #print("reading rsyslog logs : failed")
        exit(1)
    else:
        syslog.syslog("Reading Rsyslog Logs : Success")
    #move current rsyslog  file to sent
    makedirs(rsyslog_backup)
    #move files to backup folder
    if len(rsyslog_files) > 1:
        for f in range(len(rsyslog_files[:-1])):
            replace("{}/{}".format(rsyslog_dir, rsyslog_files[f]),"{}/{}".format(rsyslog_backup, rsyslog_files[f]))
    #take 2 first file
    #for file in rsyslog_files[:2]:
    #    replace("{}/{}".format(rsyslog_dir, file),"{}/{}".format(rsyslog_backup, file))

#connect to radius database and get data > rad_files, log_dir=rsyslog_backup
def rad_db(log_dir):
    rsyslog_backup_files = listdir(log_dir)
    if not path.exists(rad_files):
        makedirs(rad_files)
    for b_file in rsyslog_backup_files[:1]:
            t2 = "{}-{}-{} {}:{}:59".format(year, b_file[:2], b_file[2:4], b_file[4:6], b_file[6:8])
            t1 =datetime.strptime(t2, "%Y-%m-%d %H:%M:%S")
            t1 = t1 - timedelta(minutes=30)
            #t1 = t1 - timedelta(minutes=6)
            t2 = datetime.strptime(t2, "%Y-%m-%d %H:%M:%S")
            #print("file {} between {} <> {}".format(b_file, t1, t2))
            syslog.syslog("file {} between {} <> {}".format(b_file, t1, t2))
            if (system("clickhouse-client -d radius -q \"select * from ou  where bras like '{}' and time between '{}' and '{}' Format CSV\" > {}/{}".format(bras_name, t1, t2, rad_files, b_file))) != 0 :
                syslog.syslog("Clickhouse Error:  Unable to Fetch Data From Radius DB (radius.ou) For {}".format(b_file))
            else :
                syslog.syslog("Fetch data From Radius DB For  {} : Success".format(b_file))

#create dict from radius attr, log_dir=rsyslog_backup
def report(log_dir):
    #radius >> time,uname,sip,mac,bras,acct_st
    # radius dictionary key(sip): ...
    online = {}
    rsyslog_backup_files = listdir(log_dir)
    rad_file = listdir(rad_files)
    #open radius files > dict
    for rad in rad_file:
        with open('{}/{}'.format(rad_files, rad)) as rad_f:
            #print(rad)
            rad_csv = csv.reader(rad_f)
            for row in rad_csv:
                online[row[2]] = [row[1], row[3]]
            remove("{}/{}".format(rad_files, rad))
    makedirs('{}/{}'.format(bras_report, scrtime))
    #open bras files and save to final report
    #bras >> time,proto,sip,sport,nip,nport,dip,dport,bras
    #final report >> uname,mac,time,proto,sip,sport,nip,nport,dip,dport,bras
    for bras in rsyslog_backup_files:
        report = open("{}/{}/{}".format(bras_report, scrtime, bras), "a")
        with open("{}/{}".format(rsyslog_backup, bras)) as bras:
            bras_csv = csv.reader(bras)
            for row in bras_csv:
                #print(row, row[2])
                if row[2] in online:
                    #print(row[2], online[row[2]])
                    #print(online.get(row[2]))
                    rad =online.get(row[2])
                    #print("{},{},{},{},{},{},{},{},{},{},{}".format(rad[0], rad[1], row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8]))
                    report.write("{},{},{},{},{},{},{},{},{},{},{}\n".format(rad[0], rad[1], row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8]))
                else:
                    #print("{} not found ".format(row[2]))
                    #rad = client.execute("select * from ou where sip = {} limit 1".format(row[2]))
                    #print("rad orginal",rad)
                    #if len(rad) > 0:
                        #rad = list(rad[0])
                        #print("rad list[0]", rad)
                        #uname = rad[1]
                        #mac = rad[3]
                        #print(uname, mac)
                        #report.write("{},{},{},{},{},{},{},{},{},{},{}\n".format(uname, mac ,row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8]))
                    report.write("0,Not Found,{},{},{},{},{},{},{},{},{}\n".format(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8]))
                #break
        report.close()

#send to main database
def send2db(bras_dir):
    db_report = "{}/{}".format(bras_dir, scrtime)
    db_list = listdir(db_report)
    for report_file in db_list:
        if (system("clickhouse-client -d cgnat -q \"insert into  nat  Format CSV\" <  {}/{}".format(db_report, report_file))) != 0:
            syslog.syslog("Clickhouse Error : Unable To Send {} To DB cgnat.nat".format(report_file))
        else:
            syslog.syslog("Sending {} To DB cgnat.nat : Success ".format(report_file))

rsyslog_logs(rsyslog_dir)
rad_db(rsyslog_backup)
report(rsyslog_backup)
send2db(bras_report)

execute_t = datetime.now() - execute_t1
print(execute_t)
syslog.syslog("Bras Execution Time : {}".format(execute_t))
exit()
