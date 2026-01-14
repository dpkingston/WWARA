#!/bin/sh
DATE=$(date '+%Y%m%d-%H%M')
DEST="/Users/dpk/Google Drive/Shared drives/WWARA Administration/Finances/"
if ! test -d "${DEST}"; then
	echo Destination directory "$DEST" missing
fi

for i in Members Transactions
do
	cp -pv $i.csv "/Users/dpk/Google Drive/Shared drives/WWARA Administration/Finances/$i-$DATE.csv"
done
