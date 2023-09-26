# [How2Hack: Dashboard E-Learning & CTF Platform]

# <div align="center"> ![](https://github.com/Simostaia/Simostaia.github.io/blob/master/assets/static/logo_immagine.png?raw=true) </div> 

<!-- > **What is it?**:-->

## What is How2Hack

How2Hack is a cyber range platform designed to help penetration testers to improve their skills.

It is an all-in platform where users can read documentations and practise on most common attack type, according to CyberKillChain.

They could compete each others, trying to "exfiltrate" flags from laboratories and inserting them into the CTF platform.

![How2Hack Homepage](https://www.simonestaiano.it/assets/static/Dashboard_Simone_zoom.png)

<!-- > **What technologies are involved?**: -->
### What technologies are involved?

![Static Badge](https://img.shields.io/badge/python-3.8-blue?logo=python&labelColor=black)
![Static Badge](https://img.shields.io/badge/Docker-blue?logo=docker)
[![Badge](https://img.shields.io/badge/Django-v2.2.0-darkgreen?logo=django&labelColor=darkgreen&color=black)](https://www.djangoproject.com/)
[![Badge](https://img.shields.io/badge/CTFd-red)](https://github.com/CTFd/CTFd)
[![Badge](https://img.shields.io/badge/WebSSH-v1.6.2-black)](https://github.com/huashengdun/webssh/tree/master)
![Static Badge](https://shields.io/badge/MySQL-lightgrey?logo=mysql&style=plastic&logoColor=white&labelColor=blue)

- Laboratories are vulnerability-by-design docker containers running in a custom openVPN.

- Dashbaord is based on Django 2.2 with [a BootStrap Template](https://appseed.us/admin-dashboards/django-dashboard-material).

- CTF Platform is CTFd, based on python and Flask. CTFd provides a platform for creating, managing, and running CTF competitions.

- WebSSH is a web-based solution that provides a graphical user interface for managing SSH connections to remote servers. It allows you to access the laboratories via an SSH client directly from web broswer, without the need to install a local SSH client on your computer.

- Nginx running on port 80 of the web server acts as a reverse proxy and it's configured to route HTTP requests to the backend servers.

<!-- > **What technologies are involved?**: -->
## Setup

To set up the ideal environment for running the application, you'll need to configure the following components:

1. **Web Server (Server 1)**: The web server where our Django and Python code will run. This server serves as the primary host for our application.

2. **Manager Server (Server 2)**: The manager server, that serves as the orchestrator for our Docker Swarm cluster.

3. **Worker Server (Server 3 and More)**: Worker servers that are part of the Docker Swarm cluster. These servers execute tasks and distribute workloads orchestrated by the manager server.

Here's a step-by-step guide to setting up your environment:

### 1. Configure the Web Server

- Connect via SSH to the web server.
- Install Docker.
- Set up the web server by running the following commands:
```
git clone https://github.com/Cyber-HackAdemy-UniNa/pw2021_gruppo4.git
cd pw2021_gruppo4
docker compose up -d --pull always --build
``` 

- This command will use the Docker Compose configuration to start the necessary services:
    - The application runs on port 8000
    - The CTFd platform is hosted on port 8123.
    - WebSSH is provided on port 8888 for secure remote access.
    - A default backup will be loaded into the database.

- At the first launch, create a superuser for the application with the following command:
```
docker exec -it pw2021_gruppo4-django RUN python3 manage.py createsuperuser --username admin --email test@example.com
```
- Insert the server configurations in the admin panel.
- Insert the labs in the admin panel. They will be automatically loaded into CTFd
- Start the VPN Server from the "Gestione Server" page on the admin Dashboard.

### 2. Set Up the Manager Server

- Prepare the manager server by installing Docker and initializing it as a Docker Swarm manager. Run the following command:
```
docker swarm init --advertise-addr [YOUR_IP]
```
- Ensure that the manager server can communicate with the web server and worker servers. You can do it in the "Gestione Server" page of the admin Dashboard.

### 3. Add Worker Servers (Optional)
- If you require additional computing power, add more worker servers to the Docker Swarm cluster.
- Install Docker on each worker server and join them to the Docker Swarm managed by the manager server.
```
docker swarm join --token [YOUR_TOKEN]
```

The environment is now set up, and the application is running within the Docker Swarm cluster. You can scale the number of worker servers as necessary to handle workloads efficiently.

## Troubleshooting

To monitor the status of your servers, assess their resource utilization, and perform connectivity checks, you can conveniently access these features through the 'Server Management' page within the application administrator's dashboard.

<!-- 

## per fare dump
`python3 manage.py dumpdata --indent 3 -e admin.logentry -e auth.permission -e app.notifica -e sessions.session -e contenttypes.contenttype -o backup_buono.json`

usare `-o` e non `>`

## appunti
`python3 manage.py makemigrations` # legge il codice python e crea dei diff del database
`python3 manage.py migrate` # crea il db e/o applica le modifice dei diff al database
`python3 manage.py createsuperuser --username admin --email test@example.com` # TODO password manuale
`python3 manage.py loaddata db_json/db_tesi_docker.json`

-->