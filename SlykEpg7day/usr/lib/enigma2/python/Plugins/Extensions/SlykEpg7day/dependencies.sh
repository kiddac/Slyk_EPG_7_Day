#!/bin/sh
pyv="$(python -V 2>&1)"
echo "$pyv"
echo "Checking Dependencies"
echo
if [ -d /etc/opkg ]; then
    echo "updating feeds"
    opkg update
    echo
    if [[ $pyv =~ "Python 3" ]]; then
        echo "checking python3-multiprocessing"
        opkg install python3-multiprocessing
        echo
    else
        echo "checking python-multiprocessing"
        opkg install python-multiprocessing
        echo
    fi
else
    echo "updating feeds"
    apt-get update
    echo
    if [[ $pyv =~ "Python 3" ]]; then
        echo "checking python3-multiprocessing"
        apt-get -y install python3-multiprocessing
        echo
    else
        echo "checking python-multiprocessing"
        apt-get -y install python-multiprocessing
        echo
    fi
fi
exit 0
