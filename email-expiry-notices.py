#!/usr/bin/python3

'''
email-expiry-notices.py - generate CSV with information to trigger renewal notices

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

import csv
import datetime
import smtplib
import sys
from string import Template

EXPIRY_WINDOW = datetime.timedelta(days=92)
EXPIRATION_FIELDS = ['outfreq', 'infreq', 'tone', 'access', 'stationloc', 'areaserve', 'stn',
                    'first', 'last', 'trst', 'email', 'status', 'arrlnotes', 'expiration']
NOTIFICATION_FIELDS = EXPIRATION_FIELDS + ['id', 'sent']
SMTP_SERVER = 'smtp.gmail.com'
SMTP_CREDENTIALS = 'smtp_credentials.txt'
FROM = 'wwarasecretary@gmail.com'


def read_expiring(file):
    expiring = []

    print('Processing %s' % file)
    with open(file) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            row['id'] = row['outfreq']+':'+row['stationloc']
            #print("%s" % row)
            expiring.append(row)
    print('Read %d expiring records' % len(expiring))
    return expiring

def read_notifications(file):
    notifications = {}

    print('Processing %s' % file)
    try:
        with open(file) as csvfile:
            reader = csv.DictReader(csvfile)
            for record in reader:
                if record['id'] in notifications:
                    # this is a secondary record.  Keep the most recent sent date.
                    existing_dt = datetime.datetime.strptime(notifications[record['id']]['sent'], '%Y-%m-%d')
                    new_dt = datetime.datetime.strptime(record['sent'], '%Y-%m-%d')
                    if existing_dt > new_dt:
                        print('skipping older record for %s' % record['id'])
                        continue
                notifications[record['id']] = record
            print('Read %d records from %s' % (len(notifications), file))
    except FileNotFoundError:
        initialize_notifications(file)
        print('Initialized file %s' % file)
    return notifications

def initialize_notifications(file):
    with open(file, 'a', newline='\n') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=NOTIFICATION_FIELDS)
        writer.writeheader()

def read_template(file):
    print('Reading template %s' % file)
    with open(file) as f:
        return Template(f.read())

def read_smtp_credentials(file):
    print('Reading smtp credentials from %s' % file)
    with open(file) as f:
        line = f.read()
    return line.strip().split(' ')

def send_email(template, record, credentials):
    fromaddr = FROM
    toaddr = [record['email']]
    #toaddr = ['dpk@randomnotes.org']   # TODO: Remove when testing done
    print('%s' % record)
    msg = template.substitute(record)
    print('Sending email from %s, to %s\n%s\n\n' % (fromaddr, toaddr, msg))

    server = smtplib.SMTP_SSL(SMTP_SERVER)
    #server.set_debuglevel(1)
    server.login(credentials[0], credentials[1])
    server.sendmail(fromaddr, toaddr, msg)
    server.quit()


def write_notification(file, record):
    with open(file, 'a', newline='') as csvfile:
        record['sent'] = datetime.datetime.now().strftime('%Y-%m-%d')
        writer = csv.DictWriter(csvfile, fieldnames=NOTIFICATION_FIELDS)
        writer.writerow(record)
    print('Wrote record for %s to %s' % (record['id'], file))

def main(argv):
    expiring = []

    if len(argv) != 5:
        print('Usage: %s expiring.csv notifications.csv template.txt smtp_credentials.txt')
        print('  Sends emails to expiring entries using the template and appends to notifications.')
        print('  SMTP credentials for smtp.gmail.com are in the credentials file ("user@gmail app-password").'
        quit()

    expiring = read_expiring(argv[1])
    notifications = read_notifications(argv[2])
    template = read_template(argv[3])
    credentials = read_smtp_credentials(argv[4])
    print('%s' % credentials)
    now = datetime.datetime.now()

    for record in expiring:
        expiration_dt = datetime.datetime.strptime(record['expiration'], '%Y-%m-%d')
        #print('ID %s, expiration %s, delta %s' % (record['id'], expiration_dt, delta))

        #if expiration_dt < now:
        #    # Already expired - skip (or send and expired notice?)
        #    continue

        time_to_expiry = expiration_dt - now
        if time_to_expiry < EXPIRY_WINDOW:
            print('%s expires soon (%s)' % (record['id'], time_to_expiry))
            if record['id'] in notifications:
                #print('Found %s in notifications' % record['id'])
                notification = notifications[record['id']]
                sent_dt = datetime.datetime.strptime(notification['sent'], '%Y-%m-%d')
                sent_delta = expiration_dt - sent_dt
                if sent_delta < EXPIRY_WINDOW:
                    # already sent a notification - skip
                    #print('We already sent this notification on %s.' % notification['sent'])
                    continue
            else:
                print('%s not in notifications' % record['id'])
            send_email(template, record, credentials)
            write_notification(argv[2], record)

main(sys.argv)
