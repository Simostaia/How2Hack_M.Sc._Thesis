# vulnerable_docker_smtp

Repository per scopi accademici.

Docker per l'exploit di **SMTP** e **Postfix** per l'enumeration degli utenti.

Per maggiori informazioni: **https://github.com/zooniverse/docker-postfix**

Credits to: **https://github.com/zooniverse**

DockerHub Link: **https://hub.docker.com/repository/docker/m96dg/pw_smtp_postfix**

'''bash
docker build . -t cyberhack2021pw4/massimo_vulnerable_docker_smtp
docker run --rm -it -p 25:25 cyberhack2021pw4/massimo_vulnerable_docker_smtp
'''
