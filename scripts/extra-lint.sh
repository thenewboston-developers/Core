#!/usr/bin/env bash

set -e

FILE1=.github/workflows/master.yml
FILE2=.github/workflows/pr.yml

test -f $FILE1 || exit 0
test -f $FILE2 || exit 0

diff <(sed -n '/# QUALITY-ASSURANCE-START/,/# QUALITY-ASSURANCE-END/p' $FILE1) <(sed -n '/# QUALITY-ASSURANCE-START/,/# QUALITY-ASSURANCE-END/p' $FILE2) || (echo "QUALITY-ASSURANCE section in $FILE1 and $FILE2 is different" && false)
