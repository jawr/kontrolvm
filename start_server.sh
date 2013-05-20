#!/bin/bash
PROJECT="/srv/kontrolvm/kontrolvm/"
PIDFILE="$PROJECT/kontrolvm.pid"
if [ ! -f $PIDFILE ]; then
	cd $PROJECT
	echo 'starting server'
	python manage.py runfcgi pidfile=$PIDFILE host=127.0.0.1 port=6060
fi
