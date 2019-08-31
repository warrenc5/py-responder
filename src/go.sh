#!/bin/sh -x
cd `dirname $0`
rm responder.pid
java -jar wiremock-standalone-2.19.0.jar --port 8099 --verbose true &
python ./responder.py 
