# copiato da vpn manager, sicuramente da sistemare
import docker
import subprocess
import random
import json

from docker.api import container, network
from docker.types.services import EndpointSpec
from app.models import MacchinaAttacco, User

from app.setup_docker_client import get_docker_client

from app.models import SSHTunnel_configs

import logging
import threading

def get_porta_macchina_attacco(user_id):
    MIN_RANGE = 50000
    MAX_RANGE = 60000

    user_id = int(user_id)

    me = User.objects.get(pk=user_id)

    if len(str(me.porta_ssh)) == 0:  # non c'è alcuna porta

        random_port = random.randint(MIN_RANGE, MAX_RANGE)

        esiste_gia = User.objects.filter(porta_ssh=random_port).exists()

        if esiste_gia == True:
            while(esiste_gia):
                random_port = random.randint(MIN_RANGE, MAX_RANGE)
                esiste_gia = User.objects.filter(
                    porta_ssh=random_port).exists()
                if esiste_gia == False:
                    me.porta_ssh = str(random_port)
                    me.save()
                    break
        else:
            me.porta_ssh = str(random_port)
            me.save()

        return random_port
    else:
        return me.porta_ssh


def check_ma(user_id):
    user_id = str(user_id)

    if SSHTunnel_configs.objects.exists():
        conf = SSHTunnel_configs.objects.first()
    else:
        logging.getLogger(__name__).critical("Configurazione SSH non disponibile!")
        return

    client = get_docker_client()
    client_low = get_docker_client(low=True)

    name_ma = "ma_user_" + user_id
    network_name_user = "network_userid_"+user_id
    service_ma = None

    try:
        service_ma = client.services.get(name_ma)
        return True

    except docker.errors.APIError as e:
        logging.getLogger(__name__).critical("macchina attacco per l'utente ID: "+str(user_id) +
                                             " inesistente, dettagli:\n" + str(e.args) )
        return False

def create_ma(user_id):

    user_id = str(user_id)

    # L'SDK python per docker ha una versione standard, ed una versione "low" che permette di interagire con docker a più basso livello
    if SSHTunnel_configs.objects.exists():
        conf = SSHTunnel_configs.objects.first()
    else:
        logging.getLogger(__name__).critical("manca configurazione SSH")
        return

    client = get_docker_client()
    client_low = get_docker_client(low=True)

    chiave_ssh_utente = "Utente_" + user_id

    porta_client_utente = get_porta_macchina_attacco(user_id)

    # Nome della network custom associata all'utente
    network_name_user = "network_userid_"+user_id

    # Nome ma
    name_ma = "ma_user_" + user_id
    logging.getLogger(__name__).info("ora inizio a creare")
    # Proviamo a fare un get della network Custom dell'utente, nel caso esista già
    try:
        net = client.networks.get(network_id=network_name_user)
        logging.getLogger(__name__).info(
            "trovato network associato all'utente")
    except docker.errors.NotFound:
        # Nel caso non ci sia (poichè può essere stata eliminata dopo un tot di inutilizzo), la creiamo
        #logging.getLogger(__name__).info("la rete custom dell'utente ancora non esiste, quindi la creiamo")
        #client.networks.create(name=network_name_user, driver="bridge")

        # TODO: NELLA EXCEPT CREA LA NETWORK!! CHIEDERE A ROBERTO SE VA BENE, PER IL MOMENTO LASCIAMO COSI 
        #risposta: forse va bene così - non è vero
        logging.getLogger(__name__).info(
            "la rete overlay dell'utente ancora non esiste, quindi la creiamo")
        net = client.networks.create(name=network_name_user, driver="overlay")

    # configurazione macchina attacco da model
    conf_macchina_attacco = MacchinaAttacco.objects.first()

    #eventualmente da eliminare se adesso c'è il pull
    immagine_server = conf_macchina_attacco.docker_name

    porte = {'22/tcp': porta_client_utente}

    logging.getLogger(__name__).info("avvio kali")

    # TODO: fare pull nuova img docker pull cyber.../kali:latest
    try:
        kali_image = client_low.pull(immagine_server)
        logging.getLogger(__name__).info("pull macchina attacco ok")
    except Exception as e:
        logging.getLogger(__name__).critical("pull di macchina attacco fallito")
        logging.getLogger(__name__).critical(e.args)
    user_config = User.objects.get(pk=user_id)

    env_variables = {
        'NUOVA_PASSWORD':user_config.ssh_psw,
        'SSH_PUB_USER':user_config.ssh_pub_user
    }

    try:
        # binding porte su kali (porta client_ssh)
        porta_cssh = docker.types.EndpointSpec(ports={
            int(porta_client_utente): 22
        })

        # service macchina attacco
        service_m = client.services.create(
            immagine_server,
            networks=[network_name_user],
            name=name_ma,
            endpoint_spec=porta_cssh,
            env=env_variables
        )

    except docker.errors.APIError as e1:
        logging.getLogger(__name__).critical(
            "errore durante la creazione della macchina d'attacco: " + str(user_id) + "\nDettagli: (" + str(e1.args) + ")")
        return False

    # TODO: generazione e salvataggio della chiave ssh

    return True

def remove_ma(user_id):

    user_id = str(user_id)
    if SSHTunnel_configs.objects.exists():
        conf = SSHTunnel_configs.objects.first()
    else:
        logging.getLogger(__name__).critical("Configurazione SSH non disponibile!")
        return False

    client = get_docker_client()
    client_low = get_docker_client(low=True)

    name_ma = "ma_user_" + user_id
    network_name_user = "network_userid_"+user_id
    service_ma = client.services.get(name_ma)
    id_service = service_ma.id

    try:
        client_low.remove_service(id_service)
    except docker.errors.APIError as e:
        logging.getLogger(__name__).critical(
            "errore durante la rimozione della macchina di attacco: " + str(user_id) + "\nDettagli:\n" + str(e.args) )
        return False

    return True