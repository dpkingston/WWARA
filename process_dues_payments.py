#!/usr/bin/python3

# pylint: disable=locally-disabled, line-too-long, unspecified-encoding
'''
process_dues_payments.py - add dues payments to transactions and update member record

'''

import argparse
from datetime import date
import re
from member_utils import Members, Transactions

MEMBERS = 'Members.csv'
TRANSACTIONS = 'Transactions.csv'
DUES = '5.00'

def not_iso_date(year, month, day):
    '''Return true if date is not in ISO date format (YYYY-MM-DD).'''
    return year < 2000 or year > 9999 or month < 1 or month > 12 or day < 1 or day > 31


def main():
    '''Main program.'''
    today = date.today()
    year = today.year
    if today.month > 10:
        year += 1
    today_iso=today.isoformat()

    parser = argparse.ArgumentParser(
      description='Process dues payments by adding the transaction and updating the member record.')
    parser.add_argument('--dryrun', help='Disable actually updating files.',
                        action='store_true')
    parser.add_argument('--extend', help='If false, do not extend membership expiry for already paid up members.',
                        action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument('--members', help='CSV file with member records', default=MEMBERS)
    parser.add_argument('--transactions', help='CSV file with transaction records', default=TRANSACTIONS)
    parser.add_argument('--date', help='transaction date in ISO format (YYYY-MM-DD)', default=today_iso)
    parser.add_argument('--expiry', help='year of expiry (e.g. 2024)', default=year)
    parser.add_argument('--dues', help='dues amount (e.g. 5.00)', default=DUES)
    parser.add_argument('--donation', help='donation amount (e.g. 10.00)', default='0.00')
    parser.add_argument('callsigns', nargs='+', help='callsigns of members to update')
    args = parser.parse_args()

    # Ensure that the date provide is plauibly and ISO date.  I don't check the number days in the month.
    result = re.fullmatch(r'(\d\d\d\d)-(\d\d)-(\d\d)', args.date)
    if not result or not_iso_date(int(result.group(1)), int(result.group(2)), int(result.group(3))):
        print(f'Date "{args.date}" is not in ISO format (YYYY-MM-DD)')
        raise argparse.ArgumentError

    members = Members(args.members)
    transactions = Transactions(args.transactions)

    for call in args.callsigns:
        transaction = transactions.new(call.upper, args.date, args.dues, args.donation)
        try:
            members.update_paid_thru(call.upper, year=int(args.expiry), extend=args.extend)
            transactions.append(transaction, args.dryrun)
        except (Members.UnknownMember, Members.YearOutOfRange, Members.MemberPaidUp) as e:
            print(f'Error: {e}')
            continue
    if not args.dryrun:
        members.rewrite()

main()
