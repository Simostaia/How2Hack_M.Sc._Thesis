# -*- encoding: utf-8 -*-
"""
CyberHackAdemy 2021
"""

from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.core.exceptions import ValidationError
from itertools import chain
from django.core import serializers
from django.forms.models import model_to_dict
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import PermissionsMixin
from django.utils.crypto import get_random_string
from django.core.files import File

# gestire validate
from django.utils.translation import gettext_lazy as _

from datetime import datetime
import logging

# Create your models here.


def validate_flag(value):
    try:
        value = int(value)
    except ValueError:
        raise ValidationError("Inserire un valore numerico_1")


def validate_porta_noroot(value):
    if 1024 > value or value > 65535:
        raise ValidationError(
            _('%(value)s deve essere compresa tra 1024 e 65535'),
            params={'value': value},
        )


def validate_porta_root(value):
    if 1 > value or value > 65535:
        raise ValidationError(
            _('%(value)s deve essere compresa tra 1024 e 65535'),
            params={'value': value},
        )


def to_dict(instance):
    opts = instance._meta
    data = {}
    for f in chain(opts.concrete_fields, opts.private_fields):
        data[f.name] = f.value_from_object(instance)
    for f in opts.many_to_many:
        data[f.name] = [i.id for i in f.value_from_object(instance)]
    return data


class Notifica(models.Model):
    testo = models.CharField(max_length=120)
    link = models.CharField(max_length=220)
    # a chi è destinata la notifica (ID dell'utente - oppure TUTTI)
    destinatario = models.CharField(
        max_length=50, help_text="Inserire l'id dell utente, per mandare singolarmente una notifica a quell'utente, oppure la parola 'tutti' per mandarla a tutti gli utenti")

    class Meta:
        verbose_name = 'Notifiche'
        verbose_name_plural = 'Notifiche'
# Ogni volta che si crea una notifica, si fa il check per vedere se l'id di quella notifica esiste nella tab notifica_vista


class User(AbstractBaseUser):
    nome = models.CharField(max_length=120, default='Nome')
    cognome = models.CharField(max_length=120, default='Cognome')
    username = models.CharField(max_length=120,
                                unique=True,
                                error_messages={'unique': (
                                    "Username già utilizzato")},
                                default='test'
                                )
    password = models.CharField(max_length=120, default='pippozzo')
    # professione = models.CharField(max_length=120, default='Professione')
    email = models.EmailField(max_length=120,
                              unique=True,
                              error_messages={'unique': (
                                  "Email già utilizzata")},
                              default='example@example.com'
                              )
    data = models.DateTimeField(auto_now=False, auto_now_add=True)
    porta_vpn = models.CharField(max_length=10, default='')
    # TODO: una porta come stringa ?!?!?!?!?!? MA PORCODIO
    porta_ssh = models.CharField(max_length=5, default='')
    id_ctfd = models.CharField(max_length=10, default='')
    pwd_ctfd = models.CharField(max_length=120, default='')
    ssh_psw = models.CharField(
        max_length=120, default=get_random_string(length=119))
    ssh_pub_user = models.CharField(max_length=120, default='')
    # TODO: sistemare e fare file
    #ssh_file_prv_key = models.FieldFile()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    NOME_FIELD = 'nome'
    COGNOME_FIELD = 'cognome'
    PASSWORD_FIELD = 'password'
    # PROFESSIONE_FIELD = 'professione'
    REQUIRED_FIELDS = ['email', 'username', 'nome',
                       'cognome', 'password']

    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return False

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return False

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin


class Statistiche(models.Model):
    lab_avviati = models.IntegerField(validators=[validate_flag], default=0)
    flag_trovate = models.IntegerField(validators=[validate_flag], default=0)
    guide_lette = models.IntegerField(validators=[validate_flag], default=0)
    punteggio = models.IntegerField(validators=[validate_flag], default=0)
    user_id = models.ForeignKey(User, related_name="user_id_stat",
                                default=None, blank=True, null=True, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Statistiche dell\'utente'
        verbose_name_plural = 'Statistiche dell\'utente'


class Notifica_vista(models.Model):
    stato = models.CharField(max_length=120)  # vista
    user_id = models.ForeignKey(
        User,
        related_name="user_id",
        default=None,
        blank=True,
        null=True,
        on_delete=models.CASCADE
    )
    notifica_id = models.ForeignKey(
        Notifica,
        related_name="notifica_id",
        default=None,
        blank=True,
        null=True,
        on_delete=models.CASCADE
    )


class Tag_Args(models.Model):
    colore = models.CharField(
        max_length=7,
        unique=True,
        help_text="Inserire un colore esadecimale, esempio: #DCB50A")  # FF5733
    argomento = models.CharField(max_length=20)  # SQL Injection
    spiegazione = models.TextField(default='')

    class Meta:
        verbose_name = 'Argomenti per laboratori'
        verbose_name_plural = 'Argomenti per laboratori'

    def __str__(self):
        return self.argomento


class Tag_Level(models.Model):
    colore = models.CharField(
        max_length=7,
        unique=True,
        help_text="Inserire un colore esadecimale, esempio: #DCB50A"
    )  # FF5733
    livello = models.CharField(max_length=20)  # Difficile

    class Meta:
        verbose_name = 'Livello di difficoltà per laboratorio'
        verbose_name_plural = 'Livelli di difficoltà per laboratori'

    def __str__(self):
        return self.livello


class CTFd_configs(models.Model):
    url_API = models.CharField(max_length=220, default='http://tesi.simonestaiano.it')
    token_API = models.CharField(max_length=69)
    port_API = models.IntegerField(validators=[validate_flag], default=8123)

    class Meta:
        verbose_name = 'Configurazione per la connessione CTFd'
        verbose_name_plural = 'Configurazioni per le connessioni CTFd'


class SSHTunnel_configs(models.Model):
    FULL_PATH_SSH_KEY = models.CharField(
        max_length=220, default='/home/ubuntu/.ssh/id_RSA')
    USER_SERVER = models.CharField(max_length=64, default='ubuntu')
    DNS_NAME_SERVER = models.CharField(max_length=220, default='localhost')

    class Meta:
        verbose_name = 'Configurazione per la connessione alla macchina Docker'
        verbose_name_plural = 'Configurazioni per le connessioni alle macchine Docker'

    def save(self, *args, **kwargs):
        from app.middleware import configura_ssh_macchina
        result = configura_ssh_macchina(
            self.DNS_NAME_SERVER, self.USER_SERVER, self.FULL_PATH_SSH_KEY)
        logging.getLogger(__name__).info(
            "risultato configura_ssh_macchina in salva: {}".format(result))
        super(SSHTunnel_configs, self).save(*args, **kwargs)


class Lab(models.Model):
    nome = models.CharField(max_length=120, default='Test')
    sotto_titolo = models.CharField(max_length=120, default='Test')
    docker_name = models.CharField(max_length=120)
    descrizione = models.TextField()
    documentazione = models.TextField(default='')
    flag = models.CharField(max_length=220, default='')
    categoria = models.CharField(
        "Categoria della challenge",
        max_length=120,
        default='')
    valore_flag = models.IntegerField("Punteggio della flag",
                                      validators=[validate_flag],
                                      default=10)  # deve essere numerico
    # cap_add=["NET_ADMIN"], detach=True, ports =ports_dict, name=name_lab, auto_remove=True, network=network_name_user
    hint = models.CharField(max_length=220, default='', blank=True, null=True)
    hint_cost = models.IntegerField(
        "Costo del Hint",
        validators=[validate_flag],
        default=4,
        blank=True,
        null=True
    )

    durata_secondi = models.IntegerField(
        "Durata massima in secondi",
        validators=[validate_flag],
        default=3600,
        help_text="Esempio: 3600 secondi sono 1 ora, 300 secondi sono 5 minuti"
    )

    NET_ADMIN = 'NET_ADMIN'
    TRUE = 'True'
    FALSE = 'False'

    CAP_CHOICES = [
        (NET_ADMIN, 'Net Admin'),
    ]
    cap_add = models.CharField(
        max_length=32,
        choices=CAP_CHOICES,
        default=NET_ADMIN,
    )

    DETACH_CHOICES = [
        (TRUE, 'True'),
        (FALSE, 'False'),
    ]
    detach = models.CharField(
        max_length=32,
        choices=DETACH_CHOICES,
        default=TRUE,
    )

    AUTO_REMOVE_CHOICES = [
        (TRUE, 'True'),
        (FALSE, 'False'),
    ]
    auto_remove = models.CharField(
        max_length=32,
        choices=AUTO_REMOVE_CHOICES,
        default=TRUE,
    )

    #ARGOMENTI = serializers.serialize('json', app.Tag_Args.objects.all(), fields=('argomento'))

    #d.__setitem__(key, value)

    livello = models.ForeignKey(Tag_Level, related_name="livello_diff",
                                default=None, blank=True, null=True, on_delete=models.CASCADE)

    argomento_1 = models.ForeignKey(
        Tag_Args, related_name="argo1", default=None, blank=True, null=True, on_delete=models.CASCADE)
    argomento_2 = models.ForeignKey(
        Tag_Args, related_name="argo2", default=None, blank=True, null=True, on_delete=models.CASCADE)
    argomento_3 = models.ForeignKey(
        Tag_Args, related_name="argo3", default=None, blank=True, null=True, on_delete=models.CASCADE)
    argomento_4 = models.ForeignKey(
        Tag_Args, related_name="argo4", default=None, blank=True, null=True, on_delete=models.CASCADE)

    argomento_5 = models.ForeignKey(
        Tag_Args, related_name="argo5", default=None, blank=True, null=True, on_delete=models.CASCADE)
    argomento_6 = models.ForeignKey(
        Tag_Args, related_name="argo6", default=None, blank=True, null=True, on_delete=models.CASCADE)
    argomento_7 = models.ForeignKey(
        Tag_Args, related_name="argo7", default=None, blank=True, null=True, on_delete=models.CASCADE)
    argomento_8 = models.ForeignKey(
        Tag_Args, related_name="argo8", default=None, blank=True, null=True, on_delete=models.CASCADE)
    argomento_9 = models.ForeignKey(
        Tag_Args, related_name="argo9", default=None, blank=True, null=True, on_delete=models.CASCADE)
    argomento_10 = models.ForeignKey(
        Tag_Args, related_name="argo10", default=None, blank=True, null=True, on_delete=models.CASCADE)
    argomento_11 = models.ForeignKey(
        Tag_Args, related_name="argo11", default=None, blank=True, null=True, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        # TODO: togliere sta porcata

        from app.middleware import add_challenge, patch_flag, check_challenges, patch_challenge, patch_hint, add_hints, check_challengeHint, add_flag

        if CTFd_configs.objects.exists():
            pass
        else:
            raise ValidationError(
                'Inserire la configurazione per contattare l\'API di CTFd')

        try:

            lab = Lab.objects.get(pk=self.pk)

            #
            #  --- PATCH ED INSERIMENTO FLAG -start
            #
            if lab.valore_flag != self.valore_flag or self.flag != lab.flag:
                patch = patch_flag(self.flag, self.nome, self.categoria)

                if patch == True:
                    print("FLAG PATCHATA")
                    if self.valore_flag != lab.valore_flag:
                        challenge_id = check_challenges(
                            self.nome, self.categoria)
                        if patch_challenge(challenge_id, self.nome, self.valore_flag, self.categoria) == True:
                            print("Ho Patchato anche il valore poichè erano diversi")
                        else:
                            print("Errore nel patchare il valore della flag")
                    pass
                elif patch == "challenge non trovata":
                    print("Challenge non trovata")
                    if add_challenge(self.nome, self.valore_flag, self.categoria, self.flag) == True:
                        pass
                    else:
                        raise ValidationError(
                            'Errore dell\' API CTFd, il laboratorio non è stato aggiornato (1)')
                elif patch == "flag non trovata":
                    print("flag non trovata")
                    challenge_id = check_challenges(self.nome, self.categoria)
                    if add_flag(challenge_id, self.flag) == True:
                        pass
                    else:
                        raise ValidationError(
                            'Errore dell\' API CTFd, il laboratorio non è stato aggiornato (2)')
                else:
                    raise ValidationError(
                        'Il patch della flag non è andato a buon fine (Errore non gestito)')
            else:
                print("NON aggiorno la flag perchè sono uguali")
            # if lab.valore_flag != self.valore_flag:
            #    challenge_id=check_challenges(self.nome,self.categoria)
            #    if patch_challenge(challenge_id, self.nome, self.valore_flag, self.categoria) == True:
            #        pass
            #    else:
            #        raise ValidationError('Errore dell\' API CTFd, il laboratorio non è stato aggiornato (3)')

            #
            # --- PATCH ED INSERIMENTO FLAG - end
            #

            #
            # --- PATCH ED INSERIMENTO HINT - start
            #

            if lab.hint is not None and self.hint is not None and len(lab.hint) > 0:
                patch = patch_hint(self.hint, self.hint_cost,
                                   self.nome, self.categoria)
                if patch == True:
                    pass
                elif patch == "hint non trovato":
                    challenge_id = check_challenges(self.nome, self.categoria)
                    if add_hints(challenge_id, self.hint, self.hint_cost) == True:
                        pass
                    else:
                        raise ValidationError(
                            'Errore dell\' API CTFd, il laboratorio non è stato aggiornato (1-2)')
                else:
                    raise ValidationError('FATAL ERROR if non coperto')
            else:
                # l'hint non è mai stato aggiunto, ma effettivamente controlliamo se è > 0 per capire se aggiugnerlo o meno
                if self.hint is not None and len(self.hint) > 0:
                    challenge_id = check_challenges(self.nome, self.categoria)
                    if add_hints(challenge_id, self.hint, self.hint_cost) == True:
                        pass
                    else:
                        raise ValidationError(
                            'Errore dell\' API CTFd, il laboratorio non è stato aggiornato (2-2)')
            #
            # --- PATCH ED INSERIMENTO HINT - end
            #

        except ObjectDoesNotExist:
            #super(Lab, self).save(*args, **kwargs)
            #raise ValidationError('Questo è un nuovo laboratorio')
            if add_challenge(self.nome, self.valore_flag, self.categoria, self.flag) == True:
                pass
            else:
                raise ValidationError(
                    'Errore dell\' API CTFd, il laboratorio non è stato aggiornato (1-2)')
            pass
            if self.hint is None:
                pass  # l'aggiunta dell'hint è facoltativa
            else:
                if len(self.hint) > 0:
                    patch = patch_hint(
                        self.hint, self.hint_cost, self.nome, self.categoria)
                    if patch == True:
                        pass
                    elif patch == "hint non trovato":
                        challenge_id = check_challenges(
                            self.nome, self.categoria)
                        if add_hints(challenge_id, self.hint, self.hint_cost) == True:
                            pass
                        else:
                            raise ValidationError(
                                'Errore dell\' API CTFd, il laboratorio non è stato aggiornato (2-2)')
                    else:
                        raise ValidationError('FATAL ERROR if non coperto')

        return super(Lab, self).save(*args, **kwargs)

    def __str__(self):
        return self.nome + " - " + self.docker_name

    class Meta:
        verbose_name = 'Laboratori'
        verbose_name_plural = 'Laboratori'


class CyberKillChain(models.Model):
    intro = models.TextField(default='intro')
    recon = models.TextField(default='recon')
    weapon = models.TextField(default='weapon')
    delivery = models.TextField(default='delivery')
    exploitation = models.TextField(default='exploitation')
    installation = models.TextField(default='installation')
    command_and_control = models.TextField(default='command_and_control')
    exfiltration = models.TextField(default='exfiltration')

    def __str__(self):
        return "Cyber Kill Chain Spiegazione"


class MacchinaAttacco(models.Model):
    nome = models.CharField(max_length=120, default='Kali')
    docker_name = models.CharField(
        max_length=120, default='cyberhack2021pw4/kali:latest')
    descrizione = models.TextField(default='Docker Kali Predefinito')
    # porta_ssh_interna = models.IntegerField(validators=[validate_porta_root], default=22)
    # porta_ssh_esterna = models.IntegerField(validators=[validate_porta_noroot], default=4000)
    username = models.CharField(max_length=120, default='root')
    timer_ma = models.IntegerField(
        "Timer sessione utente (in secondi)",
        validators=[validate_flag],
        default=10800,
        help_text="Esempio: 3600 secondi sono 1 ora, 300 secondi sono 5 minuti"
    )

    class Meta:
        verbose_name = 'Macchina di Attacco'
        verbose_name_plural = 'Macchine di Attacco'


class WebSSH(models.Model):
    webssh_server = models.CharField(
        max_length=120, default='http://3.89.188.106:8888')

    class Meta:
        verbose_name = 'webssh'
        verbose_name_plural = 'webssh'


class Settings_Server(models.Model):
    #SSH_key_pub = models.CharField(max_length=256, default='')

    class Meta:
        verbose_name = 'Setting Server'
        verbose_name_plural = 'Setting Server'
