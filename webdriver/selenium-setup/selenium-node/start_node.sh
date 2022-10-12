#!/usr/bin/env bash
set -euo pipefail

CURDIR=$(realpath $(dirname "$0"))
PDIR=$(realpath "$CURDIR/..")

source $PDIR/env.rc

NODE_CFG=$CURDIR/nodeConfig.json
SELENIUM_BIN=$PDIR/selenium-server-standalone-3.141.59.jar

export ASAN_OPTIONS=detect_odr_violation=0
while true; do
    java -jar $SELENIUM_BIN -host $SELENIUM_NODE_ADDR -role node -nodeConfig $NODE_CFG -hub http://$SELENIUM_HUB_ADDR:4444/grid/register
done
