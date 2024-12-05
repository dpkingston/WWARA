#!/usr/bin/python3

# pylint: disable=locally-disabled, line-too-long, unspecified-encoding
'''
email-expiry-notices.py - identify needed renewal notices and generate emails

Usage: (see below)

The programs updates notifications file with entries it has successfully posted.
Errors on stdout/stderr.

Sample input:
"outfreq","infreq","tone","access","stationloc","areaserve","stn","first","last","trst","email","status","expiration"
"53.0900","51.3900","110.9","T","Shelton","MASON COUNTY","WB7OXJ","Doyle","Wilcox","WB7OXJ","wb7oxj@msn.com","OPEN","2018-09-24"
"53.4100","51.7100","100","PL","Eatonville","PUGET SOUND- SOUTH","W7PFR","Robert","Heselberg","K7MXE","k7mxe@mashell.com","OPEN","2024-01-13"
"53.4300","51.7300","100","PL","Bainbridge Island","KITSAP COUNTY","W7NPC","Robert","Nielsen","N7XY","n7xy@n7xy.net","OPEN","2023-03-10"
"145.3500","144.7500","103.5","PL","Purdy","PIERCE COUNTY- NORTH","KA7EOC","Mark","Yordy","W7BBO","w7bbo@comcast.net","OPEN","2024-03-07"
"145.4300","144.8300","88.5","PL","Silverdale","KITSAP COUNTY- NORTH","KD7WDG","Mike","Montfort","KB0SVF","safetymm@aol.com","OPEN","2024-01-08"
"145.4700","144.8700","100","PL","Capitol Peak","WASHINGTON- SW","K7CPR","Jeremy ","Prine","KC7VCG","kc7vcg@47repeater.com","OPEN","2023-05-05"

Sample output for mail-merge
outfreq,infreq,tone,access,stationloc,areaserve,stn,first,last,trst,email,status,arrlnotes,expiration
53.09,51.39,110.9,T,Shelton,MASON COUNTY,WB7OXJ,Doyle,Wilcox,WB7OXJ,foo@gmail.com,OPEN,e,9/24/18

'''

import argparse
import csv
import datetime
from email_utils import initialize_notifications, read_template, read_smtp_credentials, send_email, write_notification

EXPIRY_WINDOW = datetime.timedelta(days=92)
EXPIRATION_FIELDS = ['outfreq', 'infreq', 'tone', 'access', 'stationloc', 'areaserve', 'stn',
                    'first', 'last', 'trst', 'email', 'status', 'arrlnotes', 'expiration']
NOTIFICATION_FIELDS = EXPIRATION_FIELDS + ['id', 'sent']
SMTP_SERVER = 'smtp.gmail.com'
SMTP_CREDENTIALS = 'smtp_credentials.txt'
FROM = 'wwarasecretary@gmail.com'


def read_expiring(file):
    '''Read list of expiring coordinations, and return a list.'''
    expiring = []

    print(f"Processing {file}")
    with open(file) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            row['id'] = row['outfreq']+':'+row['stationloc']
            #print("%s" % row)
            expiring.append(row)
    print(f"Read {len(expiring)} expiring records")
    return expiring

def read_notifications(file):
    '''Read list of previous notifications, and return a dictionary if still relevant.
       The dictionary allows us to quick locate based on our generated record id.
    '''
    notifications = {}

    print(f"Processing {file}")
    try:
        with open(file) as csvfile:
            reader = csv.DictReader(csvfile)
            for record in reader:
                if record['id'] in notifications:
                    # this is a secondary record.  Keep the most recent sent date.
                    existing_dt = datetime.datetime.strptime(notifications[record['id']]['sent'], '%Y-%m-%d')
                    new_dt = datetime.datetime.strptime(record['sent'], '%Y-%m-%d')
                    if existing_dt > new_dt:
                        print(f"skipping older record for {record['id']}")
                        continue
                notifications[record['id']] = record
            print(f"Read {len(notifications)} records from {file}")
    except FileNotFoundError:
        initialize_notifications(file, NOTIFICATION_FIELDS)
        print(f"Initialized file {file}")
    return notifications

def main():
    '''Main program.'''

    parser = argparse.ArgumentParser(
      description='Sends emails to expiring entries using the template and appends to notifications.')
    parser.add_argument('--send_emails', help='Disable dry_run and actually send emails.',
                        action='store_true')
    parser.add_argument('expiring', help='CSV file with upcoming expirations')
    parser.add_argument('notifications', help='CSV file of already posted notifications')
    parser.add_argument('template', help='Text file with Python Template syntax')
    parser.add_argument('credentials', help='GMail SMTP credientials (user@gmail.com app-password)')
    args = parser.parse_args()

    expiring = read_expiring(args.expiring)
    notifications = read_notifications(args.notifications)
    template = read_template(args.template)
    credentials = read_smtp_credentials(args.credentials)
    print(f"Credentials: {credentials}")
    now = datetime.datetime.now()

    for record in expiring:
        expiration_dt = datetime.datetime.strptime(record['expiration'], '%Y-%m-%d')
        #print('ID %s, expiration %s, delta %s' % (record['id'], expiration_dt, delta))

        #if expiration_dt < now:
        #    # Already expired - skip (or send and expired notice?)
        #    continue

        time_to_expiry = expiration_dt - now
        if time_to_expiry < EXPIRY_WINDOW:
            print(f"{record['id']} expires soon ({time_to_expiry})")
            if record['id'] in notifications:
                #print(f"Found {record['id']} in notifications")
                notification = notifications[record['id']]
                sent_dt = datetime.datetime.strptime(notification['sent'], '%Y-%m-%d')
                sent_delta = expiration_dt - sent_dt
                if sent_delta < EXPIRY_WINDOW:
                    # already sent a notification - skip
                    #print(f"We already sent this notification on {notification['sent']}")
                    continue
            else:
                print(f"{record['id']} not in notifications")
            if send_email(template, record, SMTP_SERVER, credentials, FROM, args.send_emails):
                write_notification(args.notifications, record, NOTIFICATION_FIELDS)

main()
