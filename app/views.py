# -*- encoding: utf-8 -*-
"""
CyberHackAdemy 2021
"""

from django.contrib.auth.decorators import login_required
from django.db.models import query_utils
from django.http.response import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.template import loader
from django.http import HttpResponse
from django import forms, template
import json
import os
import paramiko
from django.http import Http404
from app.middleware import get_challenge_id, submit_flag
from app.lab_manage import start_ma

from app.vpn_manage import create_server_vpn, remove_server_vpn, check_server_vpn, start_vpn
from app.setup_docker_client import get_docker_client

import html

from authentication.forms import FormFlag

from .models import Tag_Level, WebSSH
from .models import Tag_Args
from .models import User, Statistiche
from .models import CyberKillChain
from .models import Lab
from .models import MacchinaAttacco
from .models import Settings_Server
from . import lab_manage as lab_manager
from . import user_manage as user_manager
from . import notification_manage as notification_manager
from django.core.exceptions import ObjectDoesNotExist
from threading import Timer
from time import sleep

from app.models import SSHTunnel_configs

import logging
from datetime import datetime
from app.lab_manage import *
from app.macchina_attacco_manage import *
from app.setup_docker_client import conf_server

from app.setup_docker_client import create_server_key


@login_required(login_url="/login/")
def index(request):
    context = {}
    try:
        me = User.objects.get(pk=request.session["user_pk"])
        context["nome"] = str(me.nome).title()
    except:
        context["nome"] = "n.d."
        #html_template = loader.get_template('error-403.html')
        #context = {}
        # return HttpResponse(html_template.render(context, request))

    if request.method == "POST":
        form = FormFlag(request.POST or None)
        if form.is_valid():
            laboratorio = form.data.get("laboratorio")
            flag = form.data.get("flag")
            id_laboratorio = get_challenge_id(laboratorio)
            # me = User.objects.get(pk=request.session["user_pk"])
            response = submit_flag(me.id_ctfd, id_laboratorio, flag)
            context["response"] = response
            return JsonResponse(context)

    lab = Lab.objects.all()
    context["laboratori"] = lab
    html_template = loader.get_template('index.html')
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def pages(request):
    context = {}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:
        #print("\n\n\n\n except lastttt1")
        load_template = request.path.split('/')[-1]
        html_template = loader.get_template(load_template)
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:
        html_template = loader.get_template('error-404.html')
        return HttpResponse(html_template.render(context, request))

    except:
        print("\n\n\n\n except lastttt3")
        html_template = loader.get_template('error-500.html')
        return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def get_client_vpn(request):

    if SSHTunnel_configs.objects.exists():
        conf = SSHTunnel_configs.objects.first()

    client = get_docker_client()

    if client == None:
        return errore500(request, "Non è possibile collegarsi al manager dei container. Controllare la configurazione del server.")

    try:
        user_id = str(request.session["user_pk"])
    except:
        html_template = loader.get_template('error-403.html')
        context = {}
        return HttpResponse(html_template.render(context, request))

    cont_vpn = client.containers.get("serverVPN")
    stdout = cont_vpn.exec_run(cmd="sh -c 'cat client.ovpn'")

    context = {
        'client': bytes(stdout.output).decode("utf-8"),
    }

    html_template = loader.get_template('client.ovpn')
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def argomenti(request):
    context = {}
    page = request.get_full_path()
    pk = page.split("-")
    pk = pk[-1].split(".")
    pk_arg = pk[0]

    arg = Tag_Args.objects.get(pk=pk_arg)

    try:
        my_stats = Statistiche.objects.get(
            user_id=User.objects.get(pk=request.session["user_pk"]))
        my_stats.guide_lette = int(my_stats.guide_lette) + 1
        my_stats.save()
    except ObjectDoesNotExist:
        my_stats = Statistiche(lab_avviati=0, flag_trovate=0, guide_lette=1,
                               punteggio=0, user_id=User.objects.get(pk=request.session["user_pk"]))
        my_stats.save()

    context = {
        'argomento': arg,
    }
    html_template = loader.get_template('argomenti.html')
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def page_user(request):
    context = {}
    # print(request.user.id)
    try:
        user_me = User.objects.get(pk=request.session["user_pk"])
        if user_me.is_superuser == False:
            pass
        else:
            return redirect("/admin/")
        context = {
            'user_me': user_me,
        }
        html_template = loader.get_template('page-user.html')
        return HttpResponse(html_template.render(context, request))
    except User.DoesNotExist:
        # Loggando come admin e visualizzando la dashboard con questo try-except se si clicca su profilo ti ritorna al pannello admin
        # Da modficiare il ritorno se si vuole, ma non omettere perchè genera l'eccezione
        return redirect("/admin/")
    except KeyError:
        return redirect("/admin/")


def doc_lab(request):
    page = request.get_full_path()
    pk = page.split("-")
    pk = pk[-1].split(".")
    pk_arg = pk[0]
    context = {}
    labs = Lab.objects.get(pk=pk_arg)

    context = {
        'labs': labs,
    }

    html_template = loader.get_template('documentazione.html')
    return HttpResponse(html_template.render(context, request))


def esercizi(request):

    if SSHTunnel_configs.objects.exists():
        conf = SSHTunnel_configs.objects.first()
    else:
        logging.getLogger(__name__).critical("manca configurazione SSH")
        return errore500(request, "L'admin deve configurare il manager")
    context = {}
    labs = Lab.objects.order_by("sotto_titolo")
    args = Tag_Args.objects.all()
    livelli = Tag_Level.objects.all()
    webssh = WebSSH.objects.first()

    client = get_docker_client()

    if client == None:
        return errore500(request, "Non è possibile collegarsi al manager dei container. Controllare la configurazione del server.")

    # request.session[name_lab]
    # request.session[name_lab+"_start_time"]
    # request.session[name_lab+"_IP"]

    try:
        user_id = str(request.session["user_pk"])
    except:
        user_id = "n.d."
        return errore500(request, "L'admin non può usare questa funzionalità.")
        # TODO: sistemare
        # html_template = loader.get_template('error-403.html')
        # context = {}
        # return HttpResponse(html_template.render(context, request))

    # qui vengono gestite le POST dei pulsanti avvio/stop macchina attacco
    if request.method == "POST":
        # if("form_flag" in request.POST):
        form = FormFlag(request.POST or None)
        if form.is_valid():
            laboratorio = form.data.get("laboratorio")
            flag = form.data.get("flag")
            id_laboratorio = get_challenge_id(laboratorio)
            me = User.objects.get(pk=user_id)
            response = submit_flag(me.id_ctfd, id_laboratorio, flag)
            context["response"] = response
            return JsonResponse(context)
        data = json.load(request)
        if(data["value"] == "start_macchina_attacco"):
            result = start_ma(user_id)
            if result["success"]:
                context["success"] = True
                context["porta_macchina_attacco"] = result["port"]
                context["ip_macchina_attacco"] = conf.DNS_NAME_SERVER
            else:
                context["success"] = False
        elif (data["value"] == "stop_macchina_attacco"):
            stop_ma(user_id)
        return JsonResponse(context)

    from .lab_manage import check_container_up

    try:
        for lab in labs:
            name_lab = "labid_" + str(lab.pk) + "_userid_" + \
                str(request.session["user_pk"])
            if name_lab in request.session:
                if check_container_up(name_lab) == False:
                    print(
                        "\nHo trovato una sessione settata, per un laboratorio inesistente...provvedo a cancellare:\n")
                    try:
                        del request.session[name_lab]
                        del request.session[name_lab+"_start_time"]
                        del request.session[name_lab+"_IP"]
                        print("---Sessioni cancellate")
                    except:
                        print("---Errore nel cancellare le sessioni associate")
    except:
        # TODO: comprendere
        # TODO: sistemare
        print("errore nell'ottenimento dei riferimenti al lab")

    # vpn
    try:
        cont_vpn = client.containers.get("serverVPN")
        stdout = cont_vpn.exec_run(cmd="sh -c 'cat client.ovpn'")

        if "BEGIN PRIVATE KEY" in bytes(stdout.output).decode("utf-8"):
            vpn_status = "on"
        else:
            vpn_status = "off"
    except Exception as e:
        vpn_status = "ignoto"
        logging.getLogger(__name__).critical(
            "Errore nel controllo status VPN in esercizi.html")
        logging.getLogger(__name__).critical(e.args)

    # ip macchina attacco
    porta_macchina_attacco_attiva = "non assegnato"
    try:
        service_macchina_attacco = client.services.get("ma_user_" + user_id)
        porta_macchina_attacco_attiva = service_macchina_attacco.attrs[
            'Endpoint']['Ports'][0]['PublishedPort']
    except:
        porta_macchina_attacco_attiva = "ignoto"

    macchina_attacco_attiva = MacchinaAttacco.objects.first()

    if SSHTunnel_configs.objects.exists():
        conf = SSHTunnel_configs.objects.first()
        ip_manager = conf.DNS_NAME_SERVER
    else:
        logging.getLogger(__name__).critical("manca configurazione SSH")
        return errore500(request, "L'Admin deve creare una configurazione per SSH.")

    if macchina_attacco_attiva == None:
        logging.getLogger(__name__).critical(
            "L'Admin deve creare una macchina di attacco.")
        return errore500(request, "L'Admin deve creare una macchina di attacco.")

    # per passare al terminale web la password della macchina di attacco
    # è una schifezza ma non ci sono alternative
    user_id = None
    user = None
    try:
        user_id = str(request.session["user_pk"])
        user = User.objects.get(pk=request.session["user_pk"])
        macchina_attacco_status = check_ma(user_id)
    except Exception as e:
        logging.getLogger(__name__).critical(e.args)
        return errore500(request, "Errore nella configurazione dell'utente. L'admin deve aggiornare il database per rigenerare le credenziali di accesso per la macchina di attacco.")

    context = {
        'labs': labs,
        'args': args,
        'livelli': livelli,
        'VPN': vpn_status,
        'macchina_attacco': macchina_attacco_attiva,
        "macchina_attacco_status": macchina_attacco_status,
        'porta_macchina_attacco': porta_macchina_attacco_attiva,
        'ip_macchina_attacco': ip_manager,
        'password_macchina_attacco': user.ssh_psw,
        'ip_webssh': webssh.webssh_server
    }

    html_template = loader.get_template('esercizi.html')
    return HttpResponse(html_template.render(context, request))


def cyberkillchain(request):
    context = {}
    cyberkill = CyberKillChain.objects.get(id=1)

    context = {
        'CyberKillChain': cyberkill,
    }
    html_template = loader.get_template('cyberkillchain.html')
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login")
def core(request):
    message = ""
    from .middleware import get_stats
    try:
        user_id = str(request.session["user_pk"])
        POST_VALUES = ""
        if request.is_ajax():
            POST_VALUES = json.loads(request.POST.get('data'))
            if POST_VALUES["action"] == "start_lab" or POST_VALUES["action"] == "stop_lab":
                message = lab_manager.manage(request)
            elif POST_VALUES["action"] == "get_notifications":
                message = notification_manager.manage(request)
            elif POST_VALUES["action"] == "retrive_stats":
                message = get_stats(str(request.session["user_pk"]))
            elif POST_VALUES["action"] == "start_macchina_attacco":
                message = start_ma(user_id)
            elif POST_VALUES["action"] == "stop_macchina_attacco":
                message = stop_ma(user_id)
            else:
                message = "Unknown actions"
        else:
            message = "Not Ajax"
    except Exception as exception:
        #logging.getLogger(__name__).error("Eccezione Generata, se sei admin, non puoi lanciare i laboratori!")
        logging.getLogger(__name__).error("Eccezione in views.py core")
        logging.getLogger(__name__).error(POST_VALUES)
        logging.getLogger(__name__).error(exception)
        # TODO: ma porcobio se non la stampi come faccio a capire?!
        message = "eccezione"

    return HttpResponse(message)


@login_required(login_url="/login")
def core_user(request):
    if request.is_ajax():
        message = user_manager.manage(request)
    else:
        message = "Not Ajax"

    return HttpResponse(message)


@login_required(login_url="/login")
def mostra_stato_server(request):
    context = {}
    html_template = loader.get_template('stato-server.html')
    return HttpResponse(html_template.render(context, request))


def check_configurazione_ssh(conf_client_ssh):

    hostname = conf_client_ssh.DNS_NAME_SERVER
    myuser = conf_client_ssh.USER_SERVER
    mySSHK = conf_client_ssh.FULL_PATH_SSH_KEY
    context = {}
    output_ssh = ""
    try:
        sshcon = paramiko.SSHClient()  # will create the object
        sshcon.set_missing_host_key_policy(
            paramiko.AutoAddPolicy())  # no known_hosts error
        sshcon.connect(hostname, username=myuser,
                       key_filename=mySSHK, timeout=2)  # no passwd needed
        stdin, stdout, stderr = sshcon.exec_command(
            'top -b | head -6')  # ; docker system info
        output_ssh = stdout.readlines()
        context = {'stato_server': 'Server up', 'colore_stato': True,
                   'ip_server': hostname, 'output_ssh': output_ssh}
    except:
        output_ssh = "Errore nel collegamento ssh alla macchina"
        context = {'stato_server': 'Server non raggiungibile', 'colore_stato': False,
                   'ip_server': hostname, 'output_ssh': output_ssh}

    return context


def test_stato_server(request):
    if request.user.is_superuser:
        configurazioni = SSHTunnel_configs.objects.all()
        context = {'configurazioni_ssh': []}

        if request.method == "POST":
            data = json.load(request)
            conf = SSHTunnel_configs.objects.get(DNS_NAME_SERVER=data["payload"])
            if data["name"] == "test_connessione":
                ret = check_configurazione_ssh(conf)
                return JsonResponse(ret)
            # TODO: verificare se ho scritto bene
            if data["name"] == "configura_macchina":
                ret = conf_server(conf)
                return JsonResponse(ret)

        for configurazione in configurazioni:
            context["configurazioni_ssh"].append(
                {'ip_server': configurazione.DNS_NAME_SERVER})

        context["chiave_ssh_pub"] = "Chiave SSH non presente"

        try:
            create_server_key()  # la funzione controlla se il file già esiste...
            lines = ""
            with open(os.path.expanduser('~/.ssh/id_rsa.pub')) as f:
                lines = f.readlines()[0].split('\n')[0]
            context["chiave_ssh_pub"] = lines
        except Exception as e:
            logging.getLogger(__name__).critical(e.args)
            context["chiave_ssh_pub"] = "Errore nella creazione del file id_rsa"

        html_template = loader.get_template('stato-server.html')
        return HttpResponse(html_template.render(context, request))
    else:
        return test_errore(request=request)


def test_errore(request):
    return errore500(request=request, msg="Accesso negato :(")


def test_errore403(request):
    context = {}
    html_template = loader.get_template('error-403.html')
    return HttpResponse(html_template.render(context, request), status=403)


def test_errore404(request):
    raise Http404("Pagina non disponibile")


def errore500(request, msg):
    logging.getLogger(__name__).error("errore500")
    context = {"exception_value": msg}
    html_template = loader.get_template('error-500.html')
    return HttpResponse(html_template.render(context, request), status=500)


def test_errore_bello(request):
    esempio = datetime.now().strftime("%H:%M:%S")
    context = {"exception_value": "Descrizione errore: {}.".format(esempio)}
    html_template = loader.get_template('error-ssh.html')
    return HttpResponse(html_template.render(context, request), status=501)


def test_errore_brutto(request):
    return HttpResponse('questo qui è un errore, stampato male', status=500)


@login_required(login_url="/login/")
def create_server_vpn_view(request):
    logging.getLogger(__name__).debug("create_server_vpn_view")
    if request.user.is_superuser:
        if check_server_vpn():
            return errore500(request, "Il server VPN è già avviato.")
        # create_server_vpn()
        start_vpn()
        html_template = loader.get_template('info.html')
        context = {"info_title": "Avvio VPN in corso",
                   "info_text": "Attendere l'avvio del server VPN ..."}
        return HttpResponse(html_template.render(context, request))
    else:
        logging.getLogger(__name__).info(
            "Un utente non admin ha provato ad avviare la VPN.")
        return errore500(request, "Solo l'admin può accedere a questa pagina.")


@login_required(login_url="/login/")
def remove_server_vpn_view(request):
    logging.getLogger(__name__).info("remove_server_vpn_view")
    if request.user.is_superuser:
        if not check_server_vpn():
            return errore500(request, "Il server VPN non era avviato.")
        remove_server_vpn()
        html_template = loader.get_template('info.html')
        context = {"info_title": "Arresto VPN in corso",
                   "info_text": "Attendere l'arresto del server VPN ..."}
        return HttpResponse(html_template.render(context, request))
    else:
        logging.getLogger(__name__).info(
            "Un utente non admin ha provato a stoppare la VPN.")
        return errore500(request, "Solo l'admin può accedere a questa pagina.")
