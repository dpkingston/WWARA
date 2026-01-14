#!/usr/bin/python3

# pylint: disable=locally-disabled, line-too-long, unspecified-encoding
'''
email-expiry-notices.py - generate CSV with information to trigger renewal notices

Usage: (see below)

The programs processes the members file and determines who is currently a member
and takes on of 2 actions for each current member:
  1) if the user expires this year, send a dues reminder
  2) if the user is paid up through next year or later, send a short note stating the year they will expire.
It updates a dues_notifications file with entries it has successfully posted.
Errors on stdout/stderr.

Sample members input:
Callsign,FirstName,LastName,Email,AltEmail,PaidThru,UserLevel,Password
AA6FE,Clifton,Keely,c_keely@yahoo.com,,1900,0,NOT SET
AD7UF,Charles,Boling,ad7uf@w7msh.org,,2025,0,NOT SET
AI7EZ,Jason,Berman,jberman888@aol.com,,2026,0,NOT SET

Sample output for mail-merge
outfreq,infreq,tone,access,stationloc,areaserve,stn,first,last,trst,email,status,arrlnotes,expiration
53.09,51.39,110.9,T,Shelton,MASON COUNTY,WB7OXJ,Doyle,Wilcox,WB7OXJ,foo@gmail.com,OPEN,e,9/24/18

'''

import argparse
import csv
import datetime
import smtplib
from string import Template

MEMBER_FIELDS = ['Callsign', 'FirstName', 'LastName', 'Email', 'AltEmail', 'PaidThru',
                 'UserLevel', 'Password']
NOTIFICATION_FIELDS = MEMBER_FIELDS + ['sent']
SMTP_SERVER = '108.177.98.109'
SMTP_CREDENTIALS = 'smtp_credentials.txt'
FROM = 'wwarasecretary@gmail.com'


def read_members(file):
    '''Read list of expiring coordinations, and return a list.'''
    members = []

    print(f"Processing {file}")
    with open(file) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            members.append(row)
    print(f"Read {len(members)} member records")
    return members

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
                notifications[record['Callsign']] = record
            print(f"Read {len(notifications)} records from {file}")
    except FileNotFoundError:
        initialize_notifications(file)
        print(f"Initialized file {file}")
    return notifications

def initialize_notifications(file):
    '''Create the notifications file and write out the header line.'''
    with open(file, 'a', newline='\n') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=NOTIFICATION_FIELDS)
        writer.writeheader()

def read_template(file):
    '''Read the email template and return it as a Template object.'''
    print(f"Reading template {file}")
    with open(file) as template:
        return Template(template.read())

def read_smtp_credentials(file):
    '''Read the account (email address) and app password for Gmail SMTP.'''
    print(f"Reading smtp credentials from {file}")
    with open(file) as creds:
        line = creds.read()
    return line.strip().split(' ')

def send_email(template, record, credentials, send_emails):
    '''Create and send an email for 1 expiring coordination.
       Return true if the email was sucessfully accepted by Gmail.
    '''
    fromaddr = FROM
    toaddr = [record['Email']]
    print(f"{record}")
    msg = template.substitute(record)
    print(f"Sending email from {fromaddr}, to {toaddr}\n{msg}\n\n")

    if not send_emails:
        return False

    try:
        server = smtplib.SMTP_SSL(SMTP_SERVER)
        server.set_debuglevel(1)
        server.login(credentials[0], credentials[1])
        server.sendmail(fromaddr, toaddr, msg)
        server.quit()
    except smtplib.SMTPException:
        print(f"Failed to send mail to {toaddr}")
        return False
    else:
        return True

def write_notification(file, record):
    '''Append a single entry to the notifications file.'''
    with open(file, 'a', newline='') as csvfile:
        record['sent'] = datetime.datetime.now().strftime('%Y-%m-%d')
        writer = csv.DictWriter(csvfile, fieldnames=NOTIFICATION_FIELDS)
        writer.writerow(record)
    print(f"Wrote record for {record['Callsign']} to {file}")

def main():
    '''Main program.'''

    parser = argparse.ArgumentParser(
      description='Sends emails to expiring entries using the template and appends to notifications.')
    parser.add_argument('--send_emails', help='Disable dry_run and actually send emails.',
                        action='store_true')
    parser.add_argument('members', help='CSV file with member data')
    parser.add_argument('notifications', help='CSV file of already posted notifications')
    parser.add_argument('dues_due_template', help='Text file with Python Template syntax')
    parser.add_argument('paid_up_template', help='Text file with Python Template syntax')
    parser.add_argument('credentials', help='GMail SMTP credientials (user@gmail.com app-password)')
    args = parser.parse_args()

    members = read_members(args.members)
    notifications = read_notifications(args.notifications)
    dues_due_template = read_template(args.dues_due_template)
    paid_up_template = read_template(args.paid_up_template)
    credentials = read_smtp_credentials(args.credentials)
    print(f"Credentials: {credentials}, SMTP Server {SMTP_SERVER}")
    now = datetime.datetime.now()

    recipients = []
    need_to_notify = []
    for record in members:
        current_year = int(datetime.datetime.now().strftime('%Y'))
        paid_thru = int(record['PaidThru'])
        if paid_thru < current_year or paid_thru == 9999:
            print(f"skipping expired member {record['Callsign']} from {record['PaidThru']}")
            continue

        if paid_thru > current_year:
            template = paid_up_template
            print(f"{record['Callsign']} paid thru {paid_thru}")
        else:
            template = dues_due_template
            print(f"{record['Callsign']} expiring {paid_thru}")

        if record['Callsign'] in notifications:
            print(f"Found {record['Callsign']} in notifications, skipping send")
            continue
        print(f"{record['Callsign']} not in notifications")
        need_to_notify.append(record)
        if send_email(template, record, credentials, args.send_emails):
            write_notification(args.notifications, record)
            recipients.append(record)

    print(f'Notified {len(recipients)} of {len(need_to_notify)} members needing nofication.')
    for record in recipients:
        print(f'Notified {record["Callsign"]}, {record["FirstName"]}, {record["LastName"]}, {record["Email"]}')

main()
