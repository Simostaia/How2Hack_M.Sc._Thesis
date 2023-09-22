#!/usr/bin/env bash
################################################################################
#                                                                              #
#  DEPRECATO:                                                                  #
#                                                                              #
#  È più comodo usare docker compose                                           #
#                                                                              #
################################################################################
# 
# 
if ! command -v docker &> /dev/null
then
    echo -n "docker non è installato"
    echo -n "Lo installo? (y/n)? "
    read answer
    if [ "$answer" != "${answer#[Yy]}" ] ;then 
        # this grammar (the #[] operator) means that the variable $answer
        # where any Y or y in 1st position will be dropped if they exist.
        curl -fsSL https://get.docker.com -o get-docker.sh
        sudo sh get-docker.sh
    else
        exit
    fi
fi

if ! command -v docker-compose &> /dev/null
then
    echo "docker-compose non è installato."
    echo -n "Lo installo? (y/n)? "
    read answer
    if [ "$answer" != "${answer#[Yy]}" ] ;then
        sudo curl -SL https://github.com/docker/compose/releases/download/v2.20.3/docker-compose-linux-x86_64 -o /usr/local/bin/docker-compose
        sudo chmod +x /usr/local/bin/docker-compose
        #sudo apt-get install docker-compose-plugin # già installato
        # in realtà mo si usa "docker compose"
    else
        exit
    fi
fi

if ! command -v python3 &> /dev/null
then
    echo "python3 non è installato. Su ubuntu si installa con:"
    echo "apt install -y python3"
    echo -n "Lo eseguo? (y/n)? "
    read answer
    if [ "$answer" != "${answer#[Yy]}" ] ;then
        sudo apt update
        sudo apt install -y python3
    else
        exit
    fi
fi

if ! command -v pip || ! command -v pip3 &> /dev/null
then
    echo "ne pip ne pip3 sono installati. Su Ubuntu si installa con:"
    echo "apt install -y python3-pip"
    echo -n "Lo eseguo? (y/n)? "
    read answer
    if [ "$answer" != "${answer#[Yy]}" ] ;then
        sudo apt update
        sudo apt install -y python3-pip
    else
        exit
    fi
fi

if [ ! -d "~/webssh/" ]; then # TODO: metti come submodule
  echo "webssh non è presente."
  echo -n "Lo scarico? (y/n)? "
  read answer
    if [ "$answer" != "${answer#[Yy]}" ] ;then
        git clone https://github.com/huashengdun/webssh.git ~/webssh
        sudo python3 -m pip install tornado
    else 
        exit
    fi
fi

# TODO: metti configurazione di ctfd
echo -n "Avvio il docker di CTFd? (y/n)? "
read answer
if [ "$answer" != "${answer#[Yy]}" ] ;then
    docker run -p 8123:8000 -it --name ctfd ctfd/ctfd
fi

# aggiungi .local al PATH
#export PATH="$HOME/.local/bin:$PATH"
#pip3 install pip --upgrade

echo -n "Eseguo il setup iniziale? (y/n)"
read answer
if [ "$answer" != "${answer#[Yy]}" ] ;then
    pip3 install -r requirements.txt
    python3 manage.py makemigrations # legge il codice python e crea dei diff del database
    python3 manage.py migrate # crea il db e/o applica le modifice dei diff al database
    #echo "inserisci la password per l'utente amministratore \"admin\""
    #python3 manage.py createsuperuser --username admin --email test@example.com # TODO password manuale
    python3 manage.py loaddata db_json/db_tesi_docker.json
fi
export DEBUG=True
python3 manage.py runserver 0.0.0.0:8080
