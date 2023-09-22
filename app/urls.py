# -*- encoding: utf-8 -*-
"""
CyberHackAdemy 2021
"""

from django.urls import path, re_path
from django.views.generic import DetailView
from app.models import User
from app import views

urlpatterns = [

    # The home page
    path('',                    views.index,                    name='home'                 ),
    path('cyberkillchain.html', views.cyberkillchain,           name='cyberkillchain'       ),
    path('page-user.html',      views.page_user,                name='page_user'            ),
    path('esercizi.html',       views.esercizi,                 name='esercizi'             ),
    path('client.ovpn',         views.get_client_vpn,           name='core_user'            ),
    path('core-user/',          views.core_user,                name='core_user'            ),
    path('test_errore',         views.test_errore,              name='test_errore'          ),
    path('test_errore403',      views.test_errore403,           name='test_errore403'       ),
    path('test_errore404',      views.test_errore404,           name='test_errore404'       ),
    path('test_errore_bello',   views.test_errore_bello,        name='test_errore_bello'    ),
    path('test_errore_brutto',  views.test_errore_brutto,       name='test_errore_brutto'   ),
    path('testa-stato-server',  views.test_stato_server,        name="test_stato_server"    ),
    path('stato-server.html',   views.mostra_stato_server,      name='mostra_stato_server'  ),
    path('start-vpn',           views.create_server_vpn_view,   name='start-vpn'            ),
    path('stop-vpn',            views.remove_server_vpn_view,   name='stop-vpn'             ),


    # per vedere la spiegazione e la documentazione del lab
    re_path(r'^doc-lab-\d.html$', views.doc_lab, name='doc_lab'),
    # così si fotte il sistema
    re_path(r'^doc-lab-\d\d.html$', views.doc_lab, name='doc_lab'),
    # così si fotte il sistema anche su scala europea
    re_path(r'^doc-lab-\d\d\d.html$', views.doc_lab, name='doc_lab'),

    # Matches any html file - to be used for gentella
    # Avoid using your .html in your resources.
    # Or create a separate django app.
    re_path(r'^core/$', views.core, name='core'),
    re_path(r'^get-user-\d+\/', views.get_client_vpn, name='get_client_vpn'),
    re_path(r'^.*\.*', views.pages, name='pages'),

]
