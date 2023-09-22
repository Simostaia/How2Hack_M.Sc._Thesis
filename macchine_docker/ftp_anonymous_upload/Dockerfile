FROM alpine:3.13
RUN apk --no-cache add vsftpd

COPY start_vsftpd.sh /bin/start_vsftpd.sh
COPY vsftpd.conf /etc/vsftpd/

RUN chmod +x /bin/start_vsftpd.sh
 
EXPOSE 20 21 21000-21010

COPY flag.txt /var/ftp/flag.txt
RUN chmod +r /var/ftp/flag.txt
ENTRYPOINT ["/bin/start_vsftpd.sh"]





