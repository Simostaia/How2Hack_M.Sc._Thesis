# -*- encoding: utf-8 -*-
"""
CyberHackAdemy 2021
"""

from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.views import LogoutView
from app.lab_manage import remove_user_environment
from app.models import User
from django.forms.utils import ErrorList
from django.http import HttpResponse
from .forms import LoginForm, SignUpForm
from app.vpn_manage import check_server_vpn, create_server_vpn, remove_server_vpn
from app.middleware import *
from django.core.exceptions import ObjectDoesNotExist
import threading
import logging
from app.macchina_attacco_manage import *
from django.template import loader


def login_view(request):
    form = LoginForm(request.POST or None)

    msg = None

    if request.method == "POST":

        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                try:
                    login(request, user)
                    request.session["user_pk"] = None
                    if user.is_superuser:
                        request.session["user_pk"] = 0
                    else:
                        request.session["user_pk"] = user.pk

                        if check_userCTFd_exists(user.pk) == False:
                            logging.getLogger(__name__).info(
                                "\nL'utente su ctfd non esiste... avvio il thread\n")
                            t2 = threading.Thread(target=insert_user, args=[
                                                  user.pk], daemon=True)
                            t2.start()

                        # if check_server_vpn(user.pk) == False:
                        #     t = threading.Thread(target=create_server_vpn,args=[user.pk],daemon=True)
                        #     t.start()
                        #     return redirect("/?VPN_CREATING")

                        # if check_esecuzione_ma(user.pk) == False:
                        #     t = threading.Thread(target=create_macchina_attacco,args=[user.pk],daemon=True)
                        #     t.start()
                    # else:
                    #     return redirect("/admin/")

                    return redirect("/?success")

                except User.DoesNotExist:
                    #print("Tutto ok sir")
                    return redirect("/admin/")
            else:
                msg = 'Credenziali Errate'
        else:
            msg = 'Impossibile validare il form'

    class Meta:
        model = User

    return render(request, "accounts/login.html", {"form": form, "msg": msg})


def register_user(request):

    msg = None
    success = False

    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get("username")
            nome = form.cleaned_data.get("nome")
            cognome = form.cleaned_data.get("cognome")
            # professione = form.cleaned_data.get("professione")
            raw_password = form.cleaned_data.get("password1")
            user = authenticate(username=username, password=raw_password)

            msg = 'Utente registrato correttamente'
            success = True

            # return redirect("/login/")

        else:
            msg = 'Form non valido'
    else:
        form = SignUpForm()

    return render(request, "accounts/register.html", {"form": form, "msg": msg, "success": success})


def logout_view(request):
    pk = request.session["user_pk"]
    network_id = "network_userid_" + str(pk)
    remove_user_environment(pk, network_id)
    logout(request)
    # html_template = loader.get_template("/core/templates/accounts/login.html")
    return redirect("/login/")
