# WWARA

This repository contains scripts used to manipulate data from
the Western Washington Amateur Relay Association (wwara.org)
in support of the frequency coordination function it performs.
For example, this includes sending notices to coordination holders
up upcoming coordination expirations.

## The Process

1. Clone this repository to a local directory on machine with python3 installed

1. Fetch the expirelist90days.csv file (or other appropriately formatted file) from
   the WWARA Google Drive (WWARA Administration > Coordinations > Expiration90Days)

1. Copy the notifications.csv master file (or the lastest dated version) from Google
   Drive (WWARA Administraion > Coordinations)

1. Run a dry run pass which will not send any email or update notifications.csv
```
./email-expiry-notices.py expirelist90days.csv notifications.csv WWARA_expiry_template.txt smtp_credentials.txt > log.YYYYMMDD
```

1. Review the logfile for correctness

1. Run it for real
```
./email-expiry-notices.py --send_emails expirelist90days.csv notifications.csv WWARA_expiry_template.txt smtp_credentials.txt > log.YYYYMMDD
```

1. Upload update notifications.csv to Google Drive as notifications.YYYYMMDD

1. Upload logfile.YYYYMMDD to Google Drive (WWARA Administraion > Coordinations > Emailing Logs)
