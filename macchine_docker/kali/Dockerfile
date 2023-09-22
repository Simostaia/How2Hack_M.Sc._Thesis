FROM kalilinux/kali

# Labels
LABEL org.label-schema.schema-version="1.0"
LABEL org.label-schema.build-date=$BUILD_DATE
LABEL org.label-schema.name="cyberhack2021pw4/kali"

RUN apt-get update
RUN apt-get install -y \
    bash-completion\
    inetutils-ping curl wget ftp\
    micro\
    nano\
    net-tools\
    netcat-traditional\
    nmap\
    python3-pip\
    python3\
    ssh\
    telnet\
    vim\
    wordlists\
    zsh-autosuggestions
RUN mkdir /run/sshd /root/.ssh/

#RUN sed -i '/^#/!s/PermitRootLogin .*/PermitRootLogin yes/' /etc/ssh/sshd_config
COPY sshd_config /etc/ssh/
RUN echo "root:pippozzo" | chpasswd

# nel file start verranno lette le variabili di ambiente per 
COPY start.sh /start.sh
CMD [ "/start.sh" ]

#TODO:
# RUN DEBIAN_FRONTEND=noninteractive apt-get -y install kali-linux-headless

# ENV NUOVA_PASSWORD ""
# ENV SSH_PUB_USER ""
# TODO:
# - https://www.kali.org/docs/troubleshooting/common-minimum-setup/ temporaneamente, si potrebbero installare un  po' tutti i tools
# - 
