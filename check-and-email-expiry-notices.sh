#!/bin/bash

WORKING_DIRECTORY=/home/dpk/src/WWARA
DATE=$(date '+%Y%m%d-%H%M')
SOURCE="/home/dpk/gdrive/WWARA/Coordinations/Expiration90Days"
ADMINS="dpk@randomnotes.org kenny@holenwall.com"
LOG=email-expiry-log.$DATE

rclone mount --daemon "gdrive-wwara:" ~/gdrive/WWARA

cd $WORKING_DIRECTORY
if test $? != 0; then echo chdir to WORKING_DIRECTORY failed; exit; fi
if test ! -d "${SOURCE}"; then echo SOURCE does not exist; exit; fi

## Debugging
#echo ls "${SOURCE}"
#ls "${SOURCE}"
#echo
#echo ls -al "${SOURCE}"/expirelist90days-*.csv | sort | tail -1
#ls -al "${SOURCE}"/expirelist90days-*.csv | sort | tail -1
#echo

LATEST=$(ls "${SOURCE}"/expirelist90days-*.csv | sort | tail -1)

cleanup() {
	# Invoked when an expiry file is successfully processed.
	# We move all files to the Processed subdirectory of the SOURCE.
	# We suffix the processed file with .processed, and any others with .skipped

	file=$(basename "${LATEST}")
	mv -v "${LATEST}" "${SOURCE}"/Processed/$file.processed.$DATE
	ls "$SOURCE"/expirelist90days-*.csv | \
	while read fullfile; do
		file=$(basename "$fullfile")
		mv -v "$fullfile" "$SOURCE"/Processed/$file.skipped.$DATE
	done
	cp -pv $LOG "$SOURCE"/Logs/
	cp -pv notifications.csv notifications.$DATE.csv
	cp -pv notifications.csv "$SOURCE"/Logs/notifications.$DATE.csv
}


if test -f "${LATEST}"; then
	echo "Found latest expirelist90days: ${LATEST}"
	./email_expiry_notices.py --send_emails "${LATEST}" notifications.csv WWARA_expiry_template.txt smtp_credentials.txt > $LOG 2>&1
	if test $? == 0; then
		echo success
		grep "^Notified " $LOG | mail -s "WWARA Expiry Notice Summary" $ADMINS
		cleanup
	else
		echo failure
		mail -s "WWARA Expiry Notice Summary (Failure Detected)" $ADMINS < $LOG
	fi
else
	echo nothing to process
fi

fusermount -uz ~/gdrive/WWARA
