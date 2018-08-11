---
layout:         post
title:          DDNS Python
subtitle:       A Python-based DDNS service for client and server
author:         zrd
date:           2018-08-11
---

# DDNS Python - A Python-based DDNS service for client and server

This program acts as a set of DDNS service. On the client side, public IP address is obtained and sent to ddns server through scp.
On the server side, `dnsmasq` and `hosts` (or some other assigned file) as used to provide DDNS service. It works by checking the IPs clients sent to it and changing the `hosts` file accordingly. 

## Requirements

- Python3
- A domain at your command
- A server with `dnsmasq` and an `sudo` account (serves as ddns server)
- pip package
    - paramiko
    - scp
    - psutil

## Client side

The client will need a valid SSH user at the server, sudo privilege is NOT required. The client will need to provide a remote path to write its IP, which should be the same as the server's `path` option.

To start the client, just run

    python3 client.py

Configurations for client are written in `client.conf`.

Option          | Description 
:--------------:|:------------------------:
domain          | desired domain of the client
ddns_host       | ddns server
ssh_user        | valid ssh user at the ddns server
ssh_port        | ssh port of ddns server
ssh_password    | password of user
id_rsa          | path to identification file of user
remote_dir      | path to the directory on the ddns server to write
interval        | interval of recheck in seconds
daemon          | daemon mode

Only one of `password` and `id_rsa` is needed. Here `remote_dir` should point to the same dir as server's `path` option.

## Server side

### Add NS record to your domain

First you will have to add an NS record to your domain to assign your DDNS server to resolve the desired domain. Go to your domain's provider's page and add an NS record like

    pc    NS    ddns.yourdomain.com    600

where `ddns.yourdomain.com` should point to your ddns server about to be configured, and `pc` with suffix, like `pc.yourdomain.com` is the `domain` option on the client side.

### Configure `dnsmasq`

The server will have to install `dnsmasq` to provide resolve service. `sudo` privilege is also needed to send `SIGHUP` to `dnsmasq` service to clear its cache and update resolve.

Install `dnsmasq`

    sudo apt-get install dnsmasq

Make `dnsmasq` listen to all adresses

    sudo vim /etc/dnsmasq.conf

Modify option `listen-address`

    listen-address=(YOUR_SERVERS_PUBLIC_IP),127.0.0.1

Restart `dnsmasq`

    sudo service dnsmasq restart

### Start the server

To start the server, just run

    sudo python3 server.py

Like the client side, configurations for server are written in `server.conf`.

Option          | Description 
:--------------:|:------------------------:
path            | path to the directory on the ddns server to write
interval        | interval of recheck in seconds
daemon          | daemon mode

Now the DDNS service has been set up, you can access your client through `pc.yourdomain.com`.