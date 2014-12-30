#!/bin/bash

if [ -n "$(grep 130.199.1.1 /etc/resolv.conf)" ] ; then # BNL
    export ftp_proxy=http://192.168.1.165:3128/
    export FTP_PROXY=http://192.168.1.165:3128/
fi

source "$HOME/venv/bin/activate"

