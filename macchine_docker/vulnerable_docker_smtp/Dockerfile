FROM ubuntu:14.04

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update && \
    apt-get -y upgrade && \
    apt-get -y -q install postfix rsyslog ca-certificates
	
COPY smtp-user-enum.pl /files/
COPY users.txt /files/



EXPOSE 25

RUN adduser --disabled-password --gecos "" pluto

ADD start.sh /

ENTRYPOINT [ "/start.sh" ]
