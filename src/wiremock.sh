#!/bin/sh -x
cd `dirname $0`
java $JAVA_OPTS -jar wiremock-standalone-2.19.0.jar --port 8099 --verbose true
