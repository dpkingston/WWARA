#!/usr/bin/python3

# pylint: disable=locally-disabled, line-too-long, unspecified-encoding
'''
email-utils.py - common routines to WWARA email tools

Use this import line to utilize this file:
from email_utils import initialize_notifications, read_template, read_smtp_credentials, send_email, write_notification
'''

import csv
import datetime
import smtplib
from string import Template

def initialize_notifications(file, fieldnames):
    '''Create the notifications file and write out the header line.'''
    with open(file, 'a', newline='\n') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
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

def send_email(template, record, server, credentials, fromaddr, send_emails):
    '''Create and send an email for 1 expiring coordination.
       Return true if the email was sucessfully accepted by Gmail.
    '''
    toaddr = [record['email']]
    print(f"{record}")
    msg = template.substitute(record)
    print(f"Sending email from {fromaddr}, to {toaddr}\n{msg}\n\n")

    if not send_emails:
        return False

    try:
        server = smtplib.SMTP_SSL(server)
        #server.set_debuglevel(1)
        server.login(credentials[0], credentials[1])
        server.sendmail(fromaddr, toaddr, msg)
        server.quit()
    except smtplib.SMTPException:
        print(f"Failed to send mail to {toaddr}")
        return False

    return True

def write_notification(file, record, fieldnames):
    '''Append a single entry to the notifications file.'''
    with open(file, 'a', newline='') as csvfile:
        record['sent'] = datetime.datetime.now().strftime('%Y-%m-%d')
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writerow(record)
    print(f"Wrote record for {record['id']} to {file}")
