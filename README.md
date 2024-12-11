# WWARA

This repository contains scripts used to manipulate data from
the Western Washington Amateur Relay Association (wwara.org)
in support of the frequency coordination function it performs.
For example, this includes sending notices to coordination holders
up upcoming coordination expirations, and sending dues renewal notices.

## Coordination Related Processes

### Sending Coordination Expiry Notices

1. Clone this repository to a local directory on machine with python3 installed. If you already have a clone, use git pull to ensure its up to date.

1. Fetch the expirelist90days.csv file (or other appropriately formatted file) from
   the WWARA Google Drive (WWARA Administration > Coordinations > Expiration90Days)

1. Copy the notifications.csv master file (or the lastest dated version) from Google
   Drive (WWARA Administraion > Coordinations)

1. Run a dry run pass which will not send any email or update notifications.csv
```
./email_expiry_notices.py expirelist90days.csv notifications.csv WWARA_expiry_template.txt smtp_credentials.txt > log.YYYYMMDD
```

1. Review the logfile for correctness

1. Run it for real
```
./email_expiry_notices.py --send_emails expirelist90days.csv notifications.csv WWARA_expiry_template.txt smtp_credentials.txt > log.YYYYMMDD
```

1. Upload update notifications.csv to Google Drive as notifications.YYYYMMDD

1. Upload logfile.YYYYMMDD to Google Drive (WWARA Administraion > Coordinations > Emailing Logs)

### Sending Dues Renewal Notices

1. Clone this repository to a local directory on machine with python3 installed. If you already have a clone, use git pull to ensure its up to date.

1. Screne scrape the member list page from the Members tab of the database Web GUI for the population you want to notify (probably sort by expiry date).
   Avoid those already paid up for the coming year.  One option is to select expiring/expired members who have been members during tha last 3 years.
   A cut and paste of the lines on this page should generate a file with tab delimiters between the fields.  Place in some file like temp.txt.

1. Use tr command to convert the tabs to commas
```
tr "\t" "," < temp.txt > ExpiringMembers.csv
```

1. Examine the resulting csv file and make sure it conforms to the field headings in the next step.

1. Add this field header line to the top of the file
```
call,first,last,email,alt_email,expiry,level,flag
```

1. Pick a unique name for the notifications file, e.g. DuesNogifications-Dec2024.

1. Run a dry run pass that will not send any email or update DuesNogifications-Dec2024.csv
```
./email_dues_renewal.py ExpiringMembers.csv DuesNogifications-Dec2024.csv WWARA_dues_template.txt smtp_credentials.txt > log.test
```

1. Review the logfile for correctness.

1. Run it for real.
```
./email_dues_renewal.py --send_emails ExpiringMembers.csv DuesNogifications-Dec2024.csv WWARA_dues_template.txt smtp_credentials.txt > log.YYYYMMDD.1
```

1. Depending on how many emails your generate, you may get throttled by Gmail and your sending will start to fail.  That's OK.  Take a coffee break
   and come back in an hour or so and just re-run the same command.  The DuesNogifications-Dec2024.csv has a record of all the successfully sent
   notifications, and it won't resend them.  They are just skipped, and it will pick up sending where it started to fail earlier.

## Membership and Dues Related Processes

The master data is kept in two spreadsheets, nominally Members.csv and Transactions.csv.  process_dues_payments.py is the
first tool for managing these files and allow batch processing for a set of updates such as a batch of dues payments received
on the same day for several different members (keyed by callsign).

A typical invocation to process dues payments received on the same day would look like (including --dryrun to test run first):
```
./process_dues_payments.py --dryrun --date=2024-12-08 KC7GR W7KWS K7FW WA7CHF AC7MD AD7AV
  Member KC7GR paid through 2024, year=2025, extend=True
  Updated member KC7GR now expires 2025
  append_transaction dryrun: {'Callsign': 'KC7GR', 'Date': '2024-12-08', 'Amount': '5.00', 'Donate': '0.00', 'Trans No': '2317'}
  Member W7KWS paid through 2005, year=2025, extend=True
  Updated member W7KWS now expires 2025
  append_transaction dryrun: {'Callsign': 'W7KWS', 'Date': '2024-12-08', 'Amount': '5.00', 'Donate': '0.00', 'Trans No': '2318'}
  Member K7FW paid through 2024, year=2025, extend=True
  Updated member K7FW now expires 2025
  append_transaction dryrun: {'Callsign': 'K7FW', 'Date': '2024-12-08', 'Amount': '5.00', 'Donate': '0.00', 'Trans No': '2319'}
  Member WA7CHF paid through 2024, year=2025, extend=True
  Updated member WA7CHF now expires 2025
  append_transaction dryrun: {'Callsign': 'WA7CHF', 'Date': '2024-12-08', 'Amount': '5.00', 'Donate': '0.00', 'Trans No': '2320'}
  Member AC7MD paid through 2024, year=2025, extend=True
  Updated member AC7MD now expires 2025
  append_transaction dryrun: {'Callsign': 'AC7MD', 'Date': '2024-12-08', 'Amount': '5.00', 'Donate': '0.00', 'Trans No': '2321'}
  Member AD7AV paid through 2024, year=2025, extend=True
  Updated member AD7AV now expires 2025
  append_transaction dryrun: {'Callsign': 'AD7AV', 'Date': '2024-12-08', 'Amount': '5.00', 'Donate': '0.00', 'Trans No': '2322'}
```
after which you can drop the --dryrun flag and process for real with:
```
./process_dues_payments.py  --date=2024-12-08 KC7GR W7KWS K7FW WA7CHF AC7MD AD7AV
  Member KC7GR paid through 2024, year=2025, extend=True
  Updated member KC7GR now expires 2025
  Member W7KWS paid through 2005, year=2025, extend=True
  Updated member W7KWS now expires 2025
  Member K7FW paid through 2024, year=2025, extend=True
  Updated member K7FW now expires 2025
  Member WA7CHF paid through 2024, year=2025, extend=True
  Updated member WA7CHF now expires 2025
  Member AC7MD paid through 2024, year=2025, extend=True
  Updated member AC7MD now expires 2025
  Member AD7AV paid through 2024, year=2025, extend=True
  Updated member AD7AV now expires 2025
```
The debugging output may get trimmed down in the future or more likely hidden behind --verbose flag.

There are several error that can occur which will generate a line beginning "Error: ", and will be self explanatory.
