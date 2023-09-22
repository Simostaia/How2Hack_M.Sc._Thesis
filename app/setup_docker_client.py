import docker
import subprocess
import time
import paramiko
import logging
import os

from paramiko.ssh_exception import SSHException

from app.models import SSHTunnel_configs

def __test_stato_server__(ssh_creds):
    # TODO: si può buttare credo
    if not isinstance( ssh_creds, SSHTunnel_configs() ):
        logging.getLogger(__name__).critical("ssh_creds non è di tipo SSHTunnel_configs")
        return False

    hostname = ssh_creds.DNS_NAME_SERVER
    myuser   = ssh_creds.USER_SERVER
    mySSHK   = ssh_creds.FULL_PATH_SSH_KEY
    sshcon   = paramiko.SSHClient()  # will create the object
    sshcon.set_missing_host_key_policy(paramiko.AutoAddPolicy()) # no known_hosts error
    sshcon.connect(hostname, username=myuser, key_filename=mySSHK) # no passwd needed
    sshcon.close()
    return True


def get_docker_client(ssh_creds=None, low=False):
    """
   todo

   :param boh ssh_creds: una conf ssh
   :param str low: usa la versione APIClient al posto di DockerClient
   """
    if not SSHTunnel_configs.objects.first():
        logging.getLogger(__name__).critical("manca la configurazione SSHTunnel_configs")
        return None

    if ssh_creds is None:
        conf_client_ssh = SSHTunnel_configs.objects.first()
        base_url_docker_ssh = 'ssh://'+conf_client_ssh.USER_SERVER+'@'+conf_client_ssh.DNS_NAME_SERVER
    else:
        Exception("NON IMPLEMENTATO") # TODO: SE PASSI UN SSH CONFIG USA QUELLO 

    # TODO: qui ci va un test per vedere se oltre alla chiave ssh che inseriamo dalla dashboard ha anche la chiave id_rsa
    try:
        if low:
            client = docker.APIClient( base_url=base_url_docker_ssh)  # low - da testare
            logging.getLogger(__name__).debug("client docker low OK")
        else:
            client = docker.DockerClient(base_url=base_url_docker_ssh)
            logging.getLogger(__name__).debug("client docker high OK")
    except Exception as e: # chiave ssh sconosciuta
        # if __test_stato_server__(conf_client_ssh):
        #     logging.getLogger(__name__).critical("ssh funziona, ma docker no...")
        # else:
        #     logging.getLogger(__name__).critical("la connessione ssh non funziona")
        logging.getLogger(__name__).critical("errore nell'autenticazione ssh per docker")
        logging.getLogger(__name__).critical( e.args )
        client=None

    return client

#Funzione per il check chiave ssh id_rsa presente sulla dashboard, se non c'è crea
def create_server_key():

    # #TODO: sorry, stiamo mischiando chiavi rsa con chiavi openssh, non va bene
    # #chiave privata
    # prv_key = paramiko.RSAKey.generate(2048)
    # f_prv_path = os.path.expanduser("~/.ssh/id_rsa")
    # f_prv = open(f_prv_path,'w')
    # prv_key.write_private_key(f_prv)
    
    # #chiave pubblica
    # pub_key = paramiko.RSAKey(f_prv)
    # paramiko.RSAKey.from_private_key_file(f_prv)
    # f_pub_path = os.path.expanduser("~/.ssh/id_rsa.pub")
    # f_pub = open(f_pub_path, 'w')
    # f_pub.write("%s %s" % (pub_key.get_name(), pub_key.get_base64()))
    # f_prv.close()
    # f_pub.close()
    # os.system("ssh-keygen -f ~/.ssh/id_rsa -N \"\"") # manco ci piace

    if not os.path.exists(os.path.expanduser('~/.ssh/id_rsa')) \
        and not os.path.exists(os.path.expanduser('~/.ssh/id_rsa.pub')):
       os.system("ssh-keygen -m PEM -t rsa -b 2048 -f ~/.ssh/id_rsa -N \"\"")
    else:
        logging.getLogger(__name__).info("la chiave ssh id_rsa già esiste")
    return
    
        
# Funzione per la configurazione del server (prima connessione ssh + append della chiave publica in authorized_keys)
def conf_server(conf_client_ssh):
    hostname = conf_client_ssh.DNS_NAME_SERVER
    myuser = conf_client_ssh.USER_SERVER
    mySSHK = conf_client_ssh.FULL_PATH_SSH_KEY

    # TODO: valutare su utilizzare os system e copy id ssh

    try:
        sshcon_aggiunta_chiavi = paramiko.SSHClient()
        sshcon_aggiunta_chiavi.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        sshcon_aggiunta_chiavi.connect(hostname, username=myuser,key_filename=mySSHK, timeout=2)
        
        f_prv_path = os.path.expanduser("~/.ssh/id_rsa")
        f_pub_path = os.path.expanduser("~/.ssh/id_rsa.pub")
        
        if not(os.path.isfile(f_prv_path)):
            create_server_key()
        
        # setting permessi della id_rsa sulla macchina dove gira il codice python
        os.chmod(f_prv_path,0o400)
        
        f = open(f_pub_path, "r")
        pub_key = f.read().strip('\n')
        f.close()
        
        #comando da eseguire per configurare il server
        command = "echo \"{}\" >> ~/.ssh/authorized_keys".format(pub_key)
        # TODO: una fantastica code injection da manuale...
        
        # TODO: Bisogna fare in modo che il server possa essere configurato UNA VOLTA SOLA,
        # quindi dopo deve scomparire il bottone o comunque non deve essere cliccabile,
        # altrimenti si incasina il file authorized_keys e lo si riempe di munnezza
        try:
            sshcon_test_connessione = paramiko.SSHClient()
            sshcon_test_connessione.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            sshcon_test_connessione.connect(hostname, username=myuser,key_filename=f_prv_path, timeout=2)
        except paramiko.ssh_exception.AuthenticationException:
            logging.getLogger(__name__).info("il client non è autorizzato al login, quindi aggiungo la chiave")
            sshcon_aggiunta_chiavi.exec_command(command)
            sshcon_aggiunta_chiavi.close()
            logging.getLogger(__name__).info("connessione ssh con chiave dashboard utente ok")
        except SSHException as e:
            logging.getLogger(__name__).critical("Errore. Configurazione del server con la chiave pubblica non riuscita. {}".format(e))
        
        logging.getLogger(__name__).info("setup_docker_client_TEMP 1 ok")
        sshcon_test_connessione = paramiko.SSHClient()
        sshcon_test_connessione.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        sshcon_test_connessione.connect(hostname, username=myuser,key_filename=f_prv_path, timeout=2)

    except Exception as e: 
        logging.getLogger(__name__).error("errore nella configurazione ssh {}".format(e))
    return {}
