#!/bin/bash -x 
cd `dirname $0`
pwd 
while [[ 1 ]]; do 
inotifywait -e modify responder.py
if [ -f 'responder.pid' ] ; then
pid=`cat responder.pid` 
kill $pid
echo "killed $pid"
rm responder.pid
fi
python2.7 responder.py &
done
