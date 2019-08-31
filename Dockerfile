FROM osbase
RUN apt-get update
RUN apt-get -y install python2.7 python-avro python-kafka python-yaml 
RUN apt-get -y install strace
ADD src /
RUN touch responder.pid
RUN rm responder.pid
ENTRYPOINT [ "./go.sh" ]
VOLUME /mappings
