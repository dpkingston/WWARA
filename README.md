# WWARA

This repository contains scripts used to manipulate data from
the Western Washington Amateur Relay Association (wwara.org)
in support of the frequency coordination function it performs.
For example, this includes sending notices to coordination holders
up upcoming coordination expirations, and sending dues renewal notices.

## The Process

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

