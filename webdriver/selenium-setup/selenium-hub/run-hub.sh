#!/usr/bin/env bash
set -euo pipefail

CURDIR=$(realpath $(dirname "$0"))
PDIR=$(realpath "$CURDIR/..")

source $PDIR/env.rc

HUB_CFG=$CURDIR/hubConfig2.json
SELENIUM_BIN=$PDIR/selenium-server-standalone-3.141.59.jar

echo "starting hub at $SELENIUM_HUB_ADDR"

while true; do
    java -jar $SELENIUM_BIN -role hub -hubConfig $HUB_CFG -host $SELENIUM_HUB_ADDR
done
