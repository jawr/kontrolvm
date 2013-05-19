#!/bin/bash
kill `cat kontrolvm.pid`
rm kontrolvm.pid
./start_server.sh
