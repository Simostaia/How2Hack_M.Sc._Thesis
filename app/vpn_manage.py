
import logging
from os import remove
import docker
import subprocess
import random
import json

from docker import client
from app.models import User

from app.setup_docker_client import get_docker_client

from app.models import SSHTunnel_configs

def remove_containers(name_container):
    if SSHTunnel_configs.objects.exists():
        conf = SSHTunnel_configs.objects.first()
    else:
        logging.getLogger(__name__).critical("Errore configurazione SSH")
        return False
    
    client_low = get_docker_client(low=True)

    try: 
        #client_low.kill(name_container)
        client_low.stop(name_container)
    except docker.errors.APIError as e:
        logging.getLogger(__name__).critical("Errore durante lo stop del container openVPN.\n")
        logging.getLogger(__name__).critical(e.args)
        return False
    
    try: 
        client_low.remove_container(name_container)
    except docker.errors.APIError as e:
        logging.getLogger(__name__).critical("Errore durante la remove del container openVPN.\n")
        logging.getLogger(__name__).critical(e.args)
        return False

    return True


def create_server_vpn():

    if SSHTunnel_configs.objects.exists():
        conf = SSHTunnel_configs.objects.first()
    else:
        logging.getLogger(__name__).critical("manca configurazione SSH")
    client = get_docker_client()
    client_low = get_docker_client(low=True)

    # url sul quale sarà attivo il server VPN (deve essere quello del manager)
    url_attuale = conf.DNS_NAME_SERVER #TODO

    nome_certificato = "certificatoVPN"
    
    #nome container
    gen_cert_container = "FaseGenerazioneCertificato"
    porta_client = "1194"
    nome_volume = "ovpn-data-pw2021" 

    # Nome del container VPN
    name_VPN = "serverVPN"

    #nome dei container
    name_c1 = "FaseUno"
    name_c2 = "FaseDue"

    # docker volume create --name $OVPN_DATA_ID
    client.volumes.create(name=nome_volume)

    immagine_server = "kylemanna/openvpn"

    volume_bindings = {
        nome_volume: {
            'bind': '/etc/openvpn',
            'mode': 'rw',
        },
    }

    envs = ["EASYRSA_BATCH=1"]

    porte = {'1194/udp': porta_client}

    # docker run -v $OVPN_DATA_ID:/etc/openvpn --log-driver=none --rm kylemanna/openvpn ovpn_genconfig -u udp://indirizzo_manager:$PORTA_CLIENT_ID
    try:
        cmd1 = "ovpn_genconfig -u udp://" + \
            url_attuale+":"+str(porta_client)
        
        cmd_setup_1 = client.containers.run (
            immagine_server,
            volumes=volume_bindings,
            command=cmd1,
            cap_add=["net_admin"],
            name = name_c1
            #auto_remove=True
        )

    except docker.errors.APIError as e1:
        logging.getLogger(__name__).critical("Errore durante la creazione dei file di configurazione openvpn_genconfig")
        logging.getLogger(__name__).critical(e1.args)
        return False

    # docker run -v $OVPN_DATA_ID:/etc/openvpn --log-driver=none --rm -e EASYRSA_BATCH=1 kylemanna/openvpn ovpn_initpki nopass
    try:
        cmd_setup_2 = client.containers.run (
            immagine_server,
            volumes=volume_bindings,
            command="ovpn_initpki nopass",
            environment=envs,
            cap_add=["net_admin"],
            auto_remove=True,
            name = name_c2
        )

    except docker.errors.APIError as e2:
        logging.getLogger(__name__).critical("Errore durante la creazione della pki")
        logging.getLogger(__name__).critical(e2.args)
        return False

    # docker run -v $OVPN_DATA_ID:/etc/openvpn -d -p $PORTA_CLIENT_ID:1194/udp --cap-add=NET_ADMIN kylemanna/openvpn
    try:
        cmd_setup_3 = client.containers.run (
            immagine_server,
            volumes=volume_bindings,
            ports=porte,
            cap_add=["net_admin"],
            detach=True,
            name=name_VPN,
            auto_remove=True
        )

    except docker.errors.APIError as e3:
        logging.getLogger(__name__).critical("Errore durante lo start del server openVPN")
        logging.getLogger(__name__).critical(e3.args)
        return False

    # docker run -v $OVPN_DATA_ID:/etc/openvpn --log-driver=none --rm kylemanna/openvpn easyrsa build-client-full $ID_UTENTE_ID nopass
    try:
        # Generazione del certificato (unico per tutti gli utenti)
        cmd_generate_certificate="easyrsa build-client-full "+nome_certificato+" nopass"

        generate_certificate = client.containers.run (
            immagine_server,
            volumes=volume_bindings,
            command=cmd_generate_certificate,
            name = gen_cert_container
            #auto_remove=True
        )
    
    except docker.errors.APIError as e3:
        logging.getLogger(__name__).critical("Errore durante la generazione del certificato openVPN")
        logging.getLogger(__name__).critical(e3.args)
        return False

       

    cont_vpn = client.containers.get("serverVPN")
    stdout = cont_vpn.exec_run(cmd="sh -c 'ovpn_getclient "+nome_certificato+" > client.ovpn'")
    stdout = cont_vpn.exec_run(cmd="sh -c 'cat client.ovpn'")
    if "BEGIN CERTIFICATE" in bytes(stdout.output).decode("utf-8"):
        print("-- File client.ovpn generato correttamente")
    else:
        logging.getLogger(__name__).critical("Errore nel Server VPN: il file generato è danneggiato: "+bytes(stdout.output).decode("utf-8"))
        return False

    #rimuove ed elimina container
    remove_containers(name_c1)
    remove_containers(name_c2)
    remove_containers(gen_cert_container)
    
    return True

# TODO: è molto tenero, ma cambiamo...
# Ho pensato di controllare se il server vpn è stato creato andando a verificare l'esistenza del volume.
# So che non è corretto, perchè è soltanto il primo step della creazione del server vpn, quindi potrebbe
# tranquillamente essere andato storto qualcosa dopo e quindi il server vpn non sarebbe stato verament
# creato. Però metodi migliori non ne ho trovati al momento, anche se sono sicuro ci siano (spero)
def check_server_vpn_created():

    if SSHTunnel_configs.objects.exists():
        conf = SSHTunnel_configs.objects.first()
    else:
        logging.getLogger(__name__).critical("Errore configurazione SSH")
        return False

    client = get_docker_client()
    client_low = get_docker_client(low=True)

    name_VPN = "serverVPN"
    nome_volume = "ovpn-data-pw2021"

    try:
        client.volumes.get(nome_volume) #verificare se il nome va bene o vuole l'ID
        return True
    except docker.errors.NotFound as e:
        logging.getLogger(__name__).critical("Il volume del server VPN non esiste\n" + str(e.args))
        return False


def check_server_vpn():

    if SSHTunnel_configs.objects.exists():
        conf = SSHTunnel_configs.objects.first()
    else:
        logging.getLogger(__name__).critical("Errore configurazione SSH")
        return False

    client = get_docker_client()
    client_low = get_docker_client(low=True)

    name_VPN = "serverVPN"

    try:
        cont_vpn = client.containers.get(name_VPN)
        logging.getLogger(__name__).debug("Status VPN:"+cont_vpn.status)
        if cont_vpn.status == "running":
            return True
        else:
            return False
    except Exception as e:
        logging.getLogger(__name__).critical("Errore nel check VPN. Il server VPN non è attivo.\n" + str(e.args))
        return False

def remove_server_vpn():
    name_VPN = "serverVPN"
    nome_volume = "ovpn-data-pw2021"

    if SSHTunnel_configs.objects.exists():
        conf = SSHTunnel_configs.objects.first()
    else:
        logging.getLogger(__name__).critical("Errore configurazione SSH")
        return False

    client = get_docker_client()
    client_low = get_docker_client(low=True)

    # Rimozione container server vpn
    remove_containers(name_VPN)

     #cmd_delete_all = "rm /etc/openvpn/pki/reqs/"+nome_certificato+".req && rm /etc/openvpn/pki/issued/" + \
        #   nome_certificato+".crt && rm /etc/openvpn/pki/private/" + \
        #   nome_certificato+".key"

    # Rimozione volume associato al container server vpn
    try:
        client_low.remove_volume(nome_volume) 
    except docker.errors.APIError as e:
        logging.getLogger(__name__).critical("Errore durante l'eliminazione del volume\n")
        logging.getLogger(__name__).critical(e.args)
        return False

    return True

def start_vpn():
    if SSHTunnel_configs.objects.exists():
        conf = SSHTunnel_configs.objects.first()
    else:
        logging.getLogger(__name__).critical("Errore configurazione SSH")
        return False

    client = get_docker_client()
    client_low = get_docker_client(low=True)

    name_VPN = "serverVPN"

    # Se il server vpn non è stato creato, allora viene chiamata la funzione che lo crea da zero
    if not(check_server_vpn_created()):
        create_server_vpn()
        logging.getLogger(__name__).info("Creazione server vpn\n")
        return True

    # Altrimenti viene soltanto riavviato il container esistente (il certificato dovrebbe già esistere,
    # quindi non dovrebbe esserci bisogno di rigenerarlo. In ogni caso, si può sempre rimuovere tutto
    # e rifare la vpn)
    # In realtà noi non lo stoppiamo mai, quindi la commento questa parte
    # Lascio solo il messaggio che dice che il server è già stato creato
    else:
        logging.getLogger(__name__).info("Server vpn già esistente\n")
        return True
        # try:
        #     restart_vpn_container = client_low.start(name_VPN)
        #     logging.getLogger(__name__).info("Server vpn avviato\n")
        #     return True
        # except docker.errors.APIError as e:
        #     logging.getLogger(__name__).critical("Errore durante il riavvio del container\n")
        #     logging.getLogger(__name__).critical(e.args)
        #     return False