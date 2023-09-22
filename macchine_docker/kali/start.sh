#!/bin/sh
echo $test
echo root:$NUOVA_PASSWORD | chpasswd
echo "Inserita nuova chiave ssh: $SSH_PUB_USER"
echo "$SSH_PUB_USER" >> /root/.ssh/authorized_keys
/usr/sbin/sshd -D
