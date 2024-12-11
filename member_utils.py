#!/usr/bin/python3

# pylint: disable=locally-disabled, line-too-long, unspecified-encoding
'''
member-utils.py - common routines to managing WWARA members and their transactions

Use this import line to utilize this file:
from member_utils import read_members, rewrite_members, read_transactions, append_transaction
'''

import csv
from datetime import date
import os


class Members():
    '''Class to manage the membership records
       Basic function allow member update, and member addition.
       Member delete is not currently supported.
    '''
    def __init__(self, file):
        self.file = file
        self.fieldnames = None
        self.members = {}
        self.read()

    class UnknownMember(Exception):
        '''Member not found.'''

    class MemberPaidUp(Exception):
        '''Member dues already paid up.'''

    class YearOutOfRange(Exception):
        '''Expiry year is out of a 10 year range from today.'''

    def read(self):
        '''Read list of members, stores dictionary of dictionarys keyed on Call'''

        with open(self.file) as csvfile:
            reader = csv.DictReader(csvfile)
            self.fieldnames = reader.fieldnames
            for row in reader:
                #print(f"{row}")
                row['First Name'] = row['First Name'].capitalize()
                row['Last Name'] = row['Last Name'].capitalize()
                if row['Paid Thru'] == '':
                    row['Paid Thru'] = '1900'
                #for field in REMOVE_FIELDS:
                #    if field in row:
                #        del row[field]
                self.members[row['Callsign']] = row
        print(f"Read {len(self.members)} members from {self.file}")

    def get_member(self, call):
        '''Returns member record (dict) or None if member is unknown'''
        return self.members.get(call, None)

    def new_member(self, callsign, firstname='', lastname='',
                   email='', alt_email='', paid_thru='0000'):
        '''Creat a new member record.
           We may track the other fields at a later date:
           organization='', phone='', alt_phone='', misc_notes='',
           address1='', address2='', city='', state='', zipcode='',
        '''
        record = {}
        record['Callsign'] = callsign
        record['First Name'] = firstname
        record['Last Name'] = lastname
        record['Email'] = email
        record['Alt Email'] = alt_email
        record['Paid Thru'] = paid_thru
        record['User Level'] = '0'
        record['Password'] = 'NOT SET'
        #record['Organization'] = organization
        #record['Address1'] = address1
        #record['Address2'] = address2
        #record['City'] = city
        #record['State'] = state
        #record['Zipcode'] = zipcode
        #record['Phone'] = phone
        #record['Alt Phone'] = alt_phone
        #record['Misc Notes'] = misc_notes
        return record

    def add_member(self, record):
        '''Added a member record (dict) to the membership dictionary.  No vetting is done.'''
        self.members[record['Callsign']] = record

    def del_member(self, call):
        '''Removed a member from the membership

           Exceptions: UnknownMember
        '''
        if call in self.members:
            del self.members[call]
        else:
            raise self.UnknownMember(f'No member with call {call}')

    def get_paid_thru(self, call):
        '''Returns the current expiry year of a member.'''
        return self.members[call]['Paid Thru']

    def update_paid_thru(self, call, year=None, extend=True):
        '''Update a members expiry date.
           If the expiry year is omitted is is set to the expiry date for renewals on the current date.
           For WWARA, that is the current year, or the next year if the dues are paid in Nov or Dec.

           Exceptions: UnknownMember for missing members,
                       YearOutOfRange for a bad year
                       MemberAlreadyPaidUp if the member is already paid for the next year unless extend is True.
        '''
        today = date.today()
        this_year = today.year
        if not year:
            year = this_year
            if today.month > 10:
                # WWARA specific: Dues paid in November bestow mwmbership thru the next year
                year += 1
        elif year < this_year or year > (this_year + 10):
            raise self.YearOutOfRange(f'Year out of range {this_year} to {this_year + 10}')

        if call not in self.members:
            raise self.UnknownMember(f'No member with call {call}')
        paid_thru = int(self.get_paid_thru(call))
        print(f'  Member {call} paid through {paid_thru}, year={year}, extend={extend}')
        if paid_thru >= year and extend is False:
            raise self.MemberPaidUp(f'Member {call} is already paid up until {paid_thru}')
        if paid_thru >= year:
            year = paid_thru + 1
        self.members[call]['Paid Thru'] = str(year)
        print(f'  Updated member {call} now expires {year}')

    def rewrite(self):
        '''Create the notifications file and write out the header line.'''
        tmp_file = 'tmp_' + self.file
        with open(tmp_file, 'w', newline='\n') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.fieldnames, extrasaction='ignore')
            writer.writeheader()
            for key in sorted(self.members.keys()):
                writer.writerow(self.members[key])
        os.rename(self.file, self.file+'.bak')
        os.rename(tmp_file, self.file)


class Transactions():
    '''Class to manage the recorded transactions'''
    def __init__(self, file):
        self.file = file
        self.last_transaction = 0
        self.transactions = []
        self.read()

    def new(self, callsign, date_paid, dues, donation):
        '''Create a new transaction record sans the transaction number.'''
        record = {}
        record['Callsign'] = callsign
        record['Date'] = date_paid
        record['Amount'] = dues
        record['Donate'] = donation
        return record

    def read(self):
        '''Read list of transactions, store array of tranaction dictionaries'''

        with open(self.file) as csvfile:
            reader = csv.DictReader(csvfile)
            self.fieldnames = reader.fieldnames
            for row in reader:
                #print(f"{row}")
                #for field in REMOVE_FIELDS:
                #    if field in row:
                #        del row[field]
                self.transactions.append(row)
                self.last_transaction = max(self.last_transaction, int(row['Trans No']))
        print(f"Read {len(self.transactions)} transactions from {self.file}")

    def append(self, transaction, dryrun=False):
        '''Create the notifications file and write out the header line.'''
        self.last_transaction += 1
        transaction['Trans No'] = str(self.last_transaction)
        self.transactions.append(transaction)
        if dryrun:
            print(f'  append_transaction dryrun: {transaction}')
            return
        with open(self.file, 'a', newline='\n') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.fieldnames, extrasaction='ignore')
            writer.writerow(transaction)
