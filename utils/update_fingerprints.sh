#! /bin/sh

#
# This script will update your 'known_hosts'
# to avoid SSH fingerprint error
#

SERVER_LIST=$(cat hosts | grep -v '^#' | tail -n +2)

for h in $SERVER_LIST; do
    ip=$(dig +short $h)
    echo "Host: $h"
    echo "IP: $ip"
    ssh-keygen -R "$h"
    ssh-keygen -R "$ip"
    ssh-keyscan -H "$ip" >> ~/.ssh/known_hosts
    ssh-keyscan -H "$h" >> ~/.ssh/known_hosts
done
