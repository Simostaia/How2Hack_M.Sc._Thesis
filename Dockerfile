FROM ubuntu:20.04

WORKDIR /app

ENV DEBIAN_FRONTEND=noninteractive

RUN apt update
RUN apt install -y \
   curl

RUN curl -fsSL https://get.docker.com -o get-docker.sh
RUN sh get-docker.sh
RUN rm get-docker.sh

RUN curl -SL https://github.com/docker/compose/releases/download/v2.20.3/docker-compose-linux-x86_64 -o /usr/local/bin/docker-compose
RUN chmod +x /usr/local/bin/docker-compose

#RUN apt install -y docker
RUN apt install -y docker-compose-plugin
RUN apt install -y python3
RUN apt install -y python3-pip

# aggiungi .local al PATH
#export PATH="$HOME/.local/bin:$PATH"
#pip3 install pip --upgrade

RUN pip3 install pip --upgrade

COPY requirements.txt /app
RUN pip3 install -r requirements.txt

COPY . /app

RUN rm db.sqlite3 || true

# crea python per classi db
RUN python3 manage.py makemigrations
# crea il db
RUN python3 manage.py migrate
#RUN python3 manage.py createsuperuser --username admin --email test@example.com
#RUN python3 manage.py loaddata db_json/????.json

ENV DEBUG=True

EXPOSE 8000
CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]
