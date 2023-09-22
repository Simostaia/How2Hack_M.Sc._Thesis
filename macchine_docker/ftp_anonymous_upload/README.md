# ftp_anonymous_login

Repository per scopi accademici.

Docker per l'exploit della **Anonymous FTP vulnerability**.

Per maggiori informazioni: **https://github.com/delfer/docker-alpine-ftp-server**

Credits to: **https://github.com/delfer**

DockerHub Link: **https://hub.docker.com/r/m96dg/pw_ftp_anonymous**

'''bash
docker build . -t cyberhack2021pw4/massimo_vulnerable_docker_ftp_anonymous
docker run --rm -it -p 20:20 -p 21:21 -p 21000-21010:21000-21010 cyberhack2021pw4/massimo_vulnerable_docker_ftp_anonymous
'''
