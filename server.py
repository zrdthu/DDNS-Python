# -*- coding: utf-8 -*-

import os
import signal
import sys
import time
import re
import psutil
import json
from utils import daemonize, timestamp2str


class Domain:

    def __init__(self, name, dir):
        self.name = name
        self.last_ip = None
        self.ip_file = '%s/%s.ddnsip' % (dir, self.name)

    def _get_ip(self):
        with open(self.ip_file, 'r') as fp:
            ip = fp.read()
            fp.close()
            return re.search(r'\d+\.\d+\.\d+\.\d+', ip).group()

    def update_ip(self):
        self.ip = self._get_ip()
        if self.last_ip != self.ip:
            self.last_ip = self.ip
            return True
        return False


class Domain_Maintainance:

    def __init__(self, path):
        self.path = path
        self.domains = self._get_domain_list()
        self.domain_names = self._get_domain_name_list()

    def _get_domain_list(self):
        domains = []
        for item in os.listdir(self.path):
            if os.path.isfile(self.path + '/' + item) and re.search(r'\.ddnsip$', item):
                domains.append(
                    Domain(re.sub(r'\.ddnsip$', '', item), self.path))
        return domains

    def _get_domain_name_list(self):
        domain_names = []
        for item in os.listdir(self.path):
            if os.path.isfile(self.path + '/' + item) and re.search(r'\.ddnsip$', item):
                domain_names.append(re.sub(r'\.ddnsip$', '', item))
        return domain_names

    def _write_hosts(self):
        lines = []
        with open('/etc/hosts', 'r') as hosts:
            lines = hosts.readlines()
            for domain in self.domains:
                matched = False
                for i in range(len(lines)):
                    domain_name_reg = '\\s+' + \
                        domain.name.replace(
                            '-', '\\-').replace('_', '\\_').replace('.', '\\.')
                    if re.search(domain_name_reg, lines[i], re.RegexFlag.IGNORECASE):
                        lines[i] = re.sub(r'\d+\.\d+\.\d+\.\d+', domain.ip, lines[i])
                        matched = True
                if not matched:
                    lines.append('%s %s\n' % (domain.ip, domain.name))

        with open('/etc/hosts', 'w') as hosts:
            print('%s: writing hosts' % timestamp2str(time.time()))
            hosts.writelines(lines)

    def update(self):
        new_domain_names = self._get_domain_name_list()

        for domain in self.domains:
            if domain.name not in new_domain_names:
                self.domains.remove(domain)
                self.domain_names.remove(domain.name)

        for name in new_domain_names:
            if name not in self.domain_names:
                self.domain_names.append(name)
                self.domains.append(Domain(name, self.path))

        domain_updated = False
        for domain in self.domains:
            if domain.update_ip():
                print('%s: IP of %s changed to %s' %
                      (timestamp2str(time.time()), domain.name, domain.ip))
                domain_updated = True

        if domain_updated:
            self._write_hosts()
            return True
        else:
            return False


def update_dnsmasq():
    for pid in psutil.pids():
        if psutil.pid_exists(pid) and psutil.Process(pid).username() == 'dnsmasq':
            os.kill(pid, signal.SIGHUP)
            print('%s: dnsmasq updated' % timestamp2str(time.time()))


if __name__ == '__main__':
    conf = {}
    with open('server.conf', 'r') as fp:
        conf = json.load(fp)

    if conf['daemon'].lower() == 'true':
        daemonize(stdout='/var/log/ddns_server.log', stderr='/var/log/ddns_server_err.log')

    path = conf['path']
    interval = conf['interval']

    domain_maintainance = Domain_Maintainance(path)
    while True:
        if domain_maintainance.update():
            update_dnsmasq()
        time.sleep(interval)
