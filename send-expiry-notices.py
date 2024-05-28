#!/usr/bin/python3

'''
send-expiry-notices.py - generate CSV with information to trigger renewal notices

Usage: send-expiry-notices.py > logfile

Output will be written to notices-needed.csv, errors on stdout/stderr.

Sample input (lines split for readability:
DATA_SPEC_VERSION=2015.2.2
"FC_RECORD_ID","SOURCE","OUTPUT_FREQ","INPUT_FREQ","STATE","CITY","LOCALE","CALL","SPONSOR","CTCSS_IN","CTCSS_OUT","DCS_CDCSS",
  "DTMF","LINK","FM_WIDE","FM_NARROW","DSTAR_DV","DSTAR_DD","DMR","DMR_COLOR_CODE","FUSION","FUSION_DSQ",
  "P25_PHASE_1","P25_PHASE_2","P25_NAC","NXDN_DIGITAL","NXDN_MIXED","NXDN_RAN","ATV","DATV","RACES","ARES",
  "WX","URL","LATITUDE","LONGITUDE","EXPIRATION_DATE","COMMENT"
" 1005","WWARA","29.6800","29.5800","WA","Lookout Mtn","WASHINGTON- NORTHWEST","W7RNB","5CountyEmCommGrp","110.9","110.9","","",
  "","Y","N","N","N","N","","N","","N","N","","N","N","","N","N","N","N","N","","48.6875","-122.3625","2026-02-28",""

Sample output for mail-merge
outfreq,infreq,tone,access,stationloc,areaserve,stn,first,last,trst,email,status,arrlnotes,expiration
53.09,51.39,110.9,T,Shelton,MASON COUNTY,WB7OXJ,Doyle,Wilcox,WB7OXJ,foo@gmail.com,OPEN,e,9/24/18

'''

import csv
import datetime
import sys

EXPIRY_WINDOW = datetime.timedelta(days=92)

def read_rptrs(file):
    rptrs = []

    print('Processing %s' % file)
    with open(file) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            record = {}
            #print("%s" % row)
            record['id'] = row['FC_RECORD_ID'].strip()
            record['expiry'] = row['EXPIRATION_DATE']
            print("%s" % record)
            rptrs.append(record)
    print('Read %d rptr records' % len(rptrs))
    return rptrs

def read_notifications(file):
    notifications = {}

    print('Processing %s' % file)
    with open(file) as csvfile:
        reader = csv.DictReader(csvfile)
        for record in reader:
            notifications[record['id']] = record
    print('Read %d records from %s' % (len(notifications), file))
    return notifications

def write_expiring(outputFile, records):
    fieldnames = ['id', 'expiry', 'name', 'call', 'email', 'sent']

    with open(outputFile, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for record in records:
            record['name'] = 'name_'+record['id']
            record['call'] = 'call_'+record['id']
            record['email'] = 'email_'+record['id']
            record['sent'] = datetime.datetime.now().strftime('%Y-%m-%d')
            writer.writerow(record)
    print('Wrote %d records to %s' % (len(records), outputFile))

def main(argv):
    expiring = []

    if len(argv) != 3:
        print('Usage: %s rptrs notifications')
        print('  Writes expiring.csv')
        quit()

    rptrs = read_rptrs(argv[1])
    notifications = read_notifications(argv[2])
    now = datetime.datetime.now()
    for record in rptrs:
        expiry_dt = datetime.datetime.strptime(record['expiry'], '%Y-%m-%d')
        #print('ID %s, expiry %s, delta %s' % (record['id'], expiry_dt, delta))

        if expiry_dt < now:
            # Already expired - skip
            continue

        time_to_expiry = expiry_dt - now
        if time_to_expiry < EXPIRY_WINDOW:
            print('%s expires soon (%s)' % (record['id'], time_to_expiry))
            if record['id'] in notifications:
                notification = notifications[record['id']]
                sent_dt = datetime.datetime.strptime(notification['sent'], '%Y-%m-%d')
                sent_delta = expiry_dt - sent_dt
                if sent_delta < EXPIRY_WINDOW:
                    # already sent a notification - skip
                    continue
            expiring.append(record)
    write_expiring('expiring.csv', expiring)

main(sys.argv)
