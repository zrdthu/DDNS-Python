# -*- coding: utf-8 -*-

import time
from urllib import request, error, parse
import re
import paramiko
import json
import scp
from io import StringIO
from utils import daemonize, timestamp2str


def get_ip():
    try:
        text = request.urlopen("http://txt.go.sohu.com/ip/soip").read().decode('utf-8')
        return re.findall(r'\d+.\d+.\d+.\d+', text)[0]
    except:
        return '127.0.0.1'


def send_ip(ip, domain, hostname, username, port, ssh_password, key_filename, remote_dir):
    try:
        ssh_client = paramiko.SSHClient()
        ssh_client.load_system_host_keys()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(hostname, username=username, port=port, password=ssh_password, key_filename=key_filename)
        scp_client = scp.SCPClient(ssh_client.get_transport())
        s = StringIO(ip)
        scp_client.putfo(s, '%s/%s.ddnsip' % (remote_dir, domain))
        scp_client.close()
        s.close()
    except scp.SCPException as e:
        print(e.args)

if __name__ == '__main__':
    conf = {}
    with open('client.conf', 'r') as fp:
        conf = json.load(fp)

    if conf['daemon'].lower() == 'true':
        daemonize(stdout='/tmp/ddns_client.log', stderr='/tmp/ddns_client_err.log')


    domain = conf['domain']
    ddns_host = conf['ddns_host']
    ssh_user = conf['ssh_user']
    ssh_port = conf['ssh_port']
    ssh_password = conf['ssh_password']
    id_rsa = conf['id_rsa']
    remote_dir = conf['remote_dir']
    interval = conf['interval']

    last_ip = None

    while True:
        new_ip = get_ip()
        while last_ip == new_ip:
            new_ip = get_ip()
            time.sleep(interval)
        print('%s: IP changed from %s to %s' % (timestamp2str(time.time()), last_ip, new_ip))
        send_ip(new_ip, domain, ddns_host, ssh_user, ssh_port, ssh_password, id_rsa, remote_dir)
        last_ip = new_ip
