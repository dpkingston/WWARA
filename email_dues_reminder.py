#!/usr/bin/python3

# pylint: disable=locally-disabled, line-too-long, unspecified-encoding
'''
email-dues-reminder.py - send dues reminder emails

Usage: (see below)

The programs updates notifications file with entries it has successfully posted.
Errors on stdout/stderr.

Sample input (scraped from members list output on database web interface):
call,first,last,email,alt_email,expiry,level,flag
KB7APU,LOREN,FLINDT,morsnow@q.com,,2022,0,NOT SET
KK7RFR,DAVID,STARKEL,DLStarkel66+KK7RFR@gmail.com,,2024,0,NOT SET

Sample output for notifications file
call,first,last,email,expiry,id,sent
KB7APU,LOREN,FLINDT,morsnow@q.com,2024-12-03

'''

import argparse
import csv
from email_utils import initialize_notifications, read_template, read_smtp_credentials, send_email, write_notification

EXPIRATION_FIELDS = ['call', 'first', 'last', 'email', 'alt_email', 'expiry', 'level', 'flag']
REMOVE_FIELDS = ['alt_email', 'level', 'flag']
NOTIFICATION_FIELDS = ['call', 'first', 'last', 'email', 'expiry'] + ['id', 'sent']
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
            #print(f"{row}")
            row['first'] = row['first'].capitalize()
            row['last'] = row['last'].capitalize()
            row['id'] = row['call']
            for field in REMOVE_FIELDS:
                if field in row:
                    del row[field]
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
                #print(f"{record}")
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

    for record in expiring:
        print(f"{record['id']} expires soon")
        if record['id'] in notifications:
            print(f"We already sent notification to {record['call']} "
                   "on {notifications[record['id']]['sent']}")
            continue

        print(f"{record['id']} not in notifications")
        if send_email(template, record, SMTP_SERVER, credentials, FROM, args.send_emails):
            write_notification(args.notifications, record, NOTIFICATION_FIELDS)

main()
