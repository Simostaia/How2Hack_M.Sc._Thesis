FROM ubuntu:18.04

RUN apt update
RUN apt install -y apache2

COPY index.html /var/www/html

CMD apachectl -D FOREGROUND
