import json
import docker
import datetime
import urllib

from docker.types import services
from app.setup_docker_client import get_docker_client
from app.notification_manage import insert_notification
from .models import Lab, Statistiche, User
from django.core.exceptions import ObjectDoesNotExist
from threading import Timer

from ipaddress import IPv4Interface
from app.models import SSHTunnel_configs

from app.macchina_attacco_manage import *

import logging

# TODO:

# IMPLEMENTARE TIMER CHE STOPPA AUTOMATICAMENTE TUTTO DOPO UN DET.TEMPO
# SPAWNING DEL PROCESSO CHE CONTROLLA L'UTENZA
# push route indirizzo ip subnet e la mask  PATH di CONF profilizzata /etc/openVPN/ccd

# Funzione equivalente a decodeURIComponent di javascript


def decode_input(inputs):

    RETURNED = {}

    for key, value in inputs.items():
        RETURNED[key] = urllib.parse.unquote(value)

    return RETURNED

#cont_vpn = client.containers.get("serverVPN")
#stdout = cont_vpn.exec_run(cmd="ovpn_getclient user01")


def manage(request):
    # is_ajax è una funzione già fatta da Django che controlla la presenza dell'header HTTP_X_REQUESTED_WITH nella richiesta HTTP
    if request.is_ajax():

        if SSHTunnel_configs.objects.exists():
            conf = SSHTunnel_configs.objects.first()
        else:
            logging.getLogger(__name__).critical("manca configurazione SSH")
            return

        # L'SDK python per docker ha una versione standard, ed una versione "low" che permette di interagire con docker a più basso livello
        client = get_docker_client()
        client_low = get_docker_client(low=True)

        # creo una data corretta che servirà successivamente (il sistema attuale è 2 ore indietro, quindi qui ne aggiungo 2)
        # TODO: LE TIMEZONE PORCOBIO
        x = datetime.datetime.now() + datetime.timedelta(hours=2)

        message = ""

        # I messaggi inviati dal frontend vengono concatenati come una stringa JSON
        POST_VALUES = decode_input(json.loads(request.POST.get('data')))

        # prendo dal db il lab che ha come primary key POST_VALUES["lab"]
        try:
            laboratory = Lab.objects.get(pk=POST_VALUES["lab"])
        except:
            response_list = {
                "error": "Impossibile trovare il laboratorio"
            }
            message = json.dumps(response_list)

            return message

        ######################################################################
        #                                                                    #
        #                   INIZIO CONFIGURAZIONI VARIABILI                  #
        #                                                                    #
        ######################################################################

        # Gestore stopping_Thread dei Laboratori
        pool_threads = {}

        # Nome network custom
        network_name_user = "network_userid_" + str(request.session["user_pk"])

        # Nome del container Docker per il Laboratorio
        name_lab = "labid_" + str(laboratory.pk) + "_userid_" + \
            str(request.session["user_pk"])

        # Nome Immagine del DockerHub
        image_lab = laboratory.docker_name

        # - START - Configurazioni per il comando docker.run
        cap_lab = laboratory.cap_add

        if laboratory.detach == "True":
            detach_lab = True
        else:
            detach_lab = False

        if laboratory.auto_remove == "True":
            auto_rm_lab = True
        else:
            auto_rm_lab = False
        # - END -

        ######################################################################
        #                                                                    #
        #                   FINE CONFIGURAZIONI VARIABILI                    #
        #                                                                    #
        ######################################################################

        # Flag che serve più avanti per capire se il container in questione è già in esecuzione
        found = False

        # Fai il check se esiste già una network associata all 'utente
        # Se non esiste crea la network e fai l'attach al server VPN e restituisci il certificato all'utente
        # Poi fai l'attach del container su quella rete, e restituisci l'ip all'utente

        #client.networks.create(name, ARGS)
        #   NAME = nome_utente
        #   DRIVER = bridge
        #   INTERNAL = true ? (Restrict external access to the network.)

        response_list = {
            "": ""
        }

        try:
            ######################################################################
            #                                                                    #
            # FACCIAMO UNA SERIE DI CHECK PER VEDERE SE TUTTO L'ENVIROMENT E' OK #
            #                                                                    #
            ######################################################################

            # if check_server_vpn(str(request.session["user_pk"])) == False:
            #     response_list = {
            #         "error": "Attendere l'avvio del serverVPN"
            #     }
            #     message = json.dumps(response_list)
            #
            #     return message

            # if check_ma(str(request.session["user_pk"])) == False:
            #     response_list = {
            #         "error": "Attendere l'avvio della macchina di attacco"
            #     }
            #     message = json.dumps(response_list)

            #     return message

            ######################################################################
            #                                                                    #
            #                           END CHECKS                               #
            #                                                                    #
            ######################################################################

            # I comandi inviati dal frontend tramite AJAX
            if POST_VALUES["action"] == "start_lab" or POST_VALUES["action"] == "stop_lab":

                for serv_lab in client.services.list():
                    services_lab = client.services.get(serv_lab.short_id)

                    #print (json.dumps(contain.attrs))

                    #message = message + " <br /> imgs: " + contain.attrs['Config']['Image'] + " name:" + contain.attrs['Name']

                    # E' stato trovato il container del Lab
                    if services_lab.attrs['Spec']['TaskTemplate']['ContainerSpec']['Image'] == image_lab and services_lab.attrs['Spec']['Name'] == name_lab:
                        found = True
                        break
                    else:
                        pass
                        #print(contain.attrs['Name'] + "!=" + name_lab)

            if POST_VALUES["action"] == "start_lab":
                if(found == True):
                    if(check_container_up(name_lab)):
                        ip_service = client.services.get(name_lab)
                        lab_ip = get_ip_by_service(ip_service)
                    msg_response = "Questo laboratorio è già in esecuzione! <br />" + \
                        str(lab_ip)
                    response_list = {
                        "response_action": "stop_container",
                        "msg_response": msg_response,
                        "start_time": x.strftime("%m/%d/%Y, %H:%M:%S"),
                        "show_not": "dontshow",
                        "durata": laboratory.durata_secondi,
                        "id_timer": laboratory.pk
                    }

                elif not(check_ma(str(request.session["user_pk"]))):
                    response_list = {
                        "error": "Attendere l'avvio della macchina di attacco"
                    }
                    message = json.dumps(response_list)

                    return message

                else:
                    # Avvia il container
                    label = {"label": network_name_user}

                    lab_started = client.services.create(
                        image_lab, name=name_lab, networks=[network_name_user], labels=label)

                    # Prende l'ip del container avviato
                    lab_ip = get_ip_by_service(lab_started)

                    msg_response = "Laboratorio Avviato<br /> IP Lab: " + \
                        str(lab_ip)
                    response_list = {
                        "response_action": "stop_container",
                        "msg_response": msg_response,
                        "start_time": x.strftime("%m/%d/%Y, %H:%M:%S"),
                        "durata": laboratory.durata_secondi,
                        "id_timer": laboratory.pk
                    }

                    print(
                        "\n\n\n Starto il thread per stoppare il laboratorio "+name_lab+" tra 60 minuti")
                    # 3600 secondi sono 1 ora 300 sono 5 min
                    t = Timer(laboratory.durata_secondi, stop_lab, [
                              name_lab, laboratory.nome, request.session["user_pk"], request])  # per testing metto 15 secondi
                    pool_threads[name_lab] = t
                    t.start()  # after 30 seconds, "hello, world" will be printed

                    insert_notification(
                        "Laboratorio "+laboratory.nome+" Avviato!", "#", request.session["user_pk"])

                    try:
                        my_stats = Statistiche.objects.get(
                            user_id=User.objects.get(pk=request.session["user_pk"]))
                        my_stats.lab_avviati = int(my_stats.lab_avviati) + 1
                        my_stats.save()
                    except ObjectDoesNotExist:
                        my_stats = Statistiche(lab_avviati=1, flag_trovate=0, guide_lette=0,
                                               punteggio=0, user_id=User.objects.get(pk=request.session["user_pk"]))
                        my_stats.save()

                    # Setta la sessione che serve al frontend
                    request.session[name_lab] = "running"
                    request.session[name_lab +
                                    "_start_time"] = x.strftime("%m/%d/%Y, %H:%M:%S")
                    request.session[name_lab +
                                    "_durata"] = laboratory.durata_secondi
                    request.session[name_lab+"_IP"] = lab_ip

            elif POST_VALUES["action"] == "stop_lab":
                if(found == True):
                    print("INIZIO A STOPPARE")
                    if name_lab in pool_threads:
                        print(
                            "Esiste ancora il thread autostoppante del laboratorio, quindi ora lo killiamo e poi stoppiamo il lab")
                        pool_threads.get(name_lab).cancel()
                        del pool_threads[name_lab]
                    print("1")
                    try:
                        client_low.remove_service(name_lab)
                        msg_response = "Laboratorio Stoppato <br />"
                        print("1-1")
                    except:
                        msg_response = "Errore nel stoppare il laboratorio (1) !! <br />"
                        print("1-2")
                    print("2")
                    response_list = {
                        "msg_response": msg_response,
                        "response_action": "start_container"
                    }
                    print("3")
                    insert_notification(
                        "Laboratorio "+laboratory.nome+" Stoppato!", "#", request.session["user_pk"])
                    print("4")
                    # Togli il valore dalla sessione
                    try:
                        del request.session[name_lab]
                        del request.session[name_lab+"_start_time"]
                        del request.session[name_lab+"_IP"]
                        print("Sessione relativa al laboratorio " +
                              name_lab+" eliminata")
                    except:
                        print("Errore nel cancellare la sessione")

                    print("5")

                else:
                    # fatal error

                    try:
                        del request.session[name_lab]
                        del request.session[name_lab+"_start_time"]
                        del request.session[name_lab+"_IP"]
                    except:
                        print("Errore nel cancellare la sessione")

                    msg_response = "Laboratorio non in esecuzione !! <br />"
                    response_list = {
                        "msg_response": msg_response
                    }

        except docker.errors.NotFound as e:
            print("\n \n ---- il server non è riuscito a trovare il container VPN 1 (Provvedere ad un lancio manuale)  (" + str(e.args) + ")---- \n \n")
            response_list = {
                "error": "error1"
            }
        except docker.errors.APIError as e:
            print("\n \n ---- Errore nell'api docker 2 (" +
                  str(e.args) + ")---- \n \n")
            response_list = {
                "error": "error2"
            }

        message = json.dumps(response_list)

    else:
        message = "Not Ajax"
    return message


def get_ip_by_service(service):
    if SSHTunnel_configs.objects.exists():
        conf = SSHTunnel_configs.objects.first()
    else:
        logging.getLogger(__name__).critical("manca configurazione SSH")
        return

    client = get_docker_client()
    ip_service = None

    try:
        ip_service = service.attrs['Endpoint']['VirtualIPs'][0]['Addr']

    except docker.errors.APIError:
        print("IP del service not found")

    return ip_service

# Questa funzione viene richiamata in view.py


def check_container_up(nome_container):
    if SSHTunnel_configs.objects.exists():
        conf = SSHTunnel_configs.objects.first()
    else:
        logging.getLogger(__name__).critical("manca configurazione SSH")
        return

    client = get_docker_client()

    try:
        client.services.get(nome_container)
        return True
    except:
        return False

# Funzione che rimuove il service (docker vulnerabile) e


def stop_lab(name_lab, nome, id_user, request):

    # TODO: 'nome' viene preso dal model, name_lab sarebbe l'id? Forse si possono usare entrambi

    if SSHTunnel_configs.objects.exists():
        conf = SSHTunnel_configs.objects.first()
    else:
        logging.getLogger(__name__).critical("manca configurazione SSH")
        return

    client_low = get_docker_client(low=True)

    try:
        client_low.remove_service(name_lab)
        msg_response = "Laboratorio Stoppato<br />"
    except:
        msg_response = "Errore durante l'arresto del laboratorio<br />"

    response_list = {
        "msg_response": msg_response,
        "response_action": "start_container"
    }

    insert_notification("Laboratorio "+nome+" Stoppato!", "#", id_user)

    # Togli il valore dalla sessione
    try:
        del request.session[name_lab]
        del request.session[name_lab+"_start_time"]
        del request.session[name_lab+"_IP"]
        print("Sessione relativa al laboratorio "+name_lab+" eliminata")
    except:
        print("Errore nel cancellare la sessione")

    print("RITORNO")
    return response_list

# Funzione che rimuove una network associata ad uno specifico utente


def prune_user_network(network_id):
    if SSHTunnel_configs.objects.exists():
        conf = SSHTunnel_configs.objects.first()
    else:
        logging.getLogger(__name__).critical("manca configurazione SSH")
        return

    client_low = get_docker_client(low=True)

    try:
        client_low.remove_network(network_id)
    except docker.errors.APIError:
        print("Errore, non è stato possibile rimuovere la network associata all'utente")


def prune_networks():
    if SSHTunnel_configs.objects.exists():
        conf = SSHTunnel_configs.objects.first()
    else:
        logging.getLogger(__name__).critical("manca configurazione SSH")
        return

    client = get_docker_client()

    try:
        client.networks.prune()
    except docker.errors.APIError:
        print("\n \n ---- il server ha ritornato un errore mentre faceva i prune dei networks ---- \n \n")


def start_timer_session(pk):
    if SSHTunnel_configs.objects.exists():
        conf = SSHTunnel_configs.objects.first()
    else:
        logging.getLogger(__name__).critical("manca configurazione SSH")
        return

    client = get_docker_client()
    network_id = "network_userid_"+pk

    macchina_att = MacchinaAttacco.objects.first()
    timer_ma = Timer(macchina_att.timer_ma,
                     remove_user_environment, [pk, network_id])
    timer_ma.start()


def start_ma(pk):
    if not(check_ma(pk)):
        create_ma(pk)
        start_timer_session(pk)
        porta_client_utente = get_porta_macchina_attacco(pk)

    porta_client_utente = get_porta_macchina_attacco(pk)
    result = {
        "success": True,
        "port": porta_client_utente
    }
    return result


def stop_ma(pk):
    if check_ma(pk):
        remove_ma(pk)

# TODO: funzione da testare; va inserita in un TIMER che parte quando si avvia la macchina d'attacco
# Funzione che elimina tutto ciò che è associato ad un utente: macchina d'attacco, network, laboratori


def remove_user_environment(user_id, network_id):
    if SSHTunnel_configs.objects.exists():
        conf = SSHTunnel_configs.objects.first()
    else:
        logging.getLogger(__name__).critical("manca configurazione SSH")
        return

    client = get_docker_client()
    client_low = get_docker_client(low=True)

    # Remove dei laboratori

    label = {'label': network_id}

    containers = client.services.list()
    try:
        for container in containers:
            if (container.attrs['Spec']['Labels'] == label):
                try:
                    client_low.remove_service(container.attrs['ID'])
                except docker.errors.APIError:
                    print("Errore nella rimozione del laboratorio")
    except:
        pass
    # Remove della macchina d'attacco
    try:
        remove_ma(user_id)
    except:
        pass
    # Remove della network
    try:
        prune_user_network(network_id)
    except:
        pass
