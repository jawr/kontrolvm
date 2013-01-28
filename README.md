KontrolVM
=========

Kontrol panel for KVM

Requirements
============

* RabbitMQ - http://www.rabbitmq.com/
* Celery (3.0+) - http://www.celeryproject.org
* Bootstrap (2.2.2) - http://twitter.github.com/bootstrap/
* bootbox.js (2.4.2) - http://github.com/makeusabrew/bootbox/
* X-editable () - http://vitalets.github.com/x-editable/
* django-bootstrap-form (2.0.5) - https://github.com/tzangms/django-bootstrap-form
* django-email-as-username (1.6.2) - https://github.com/dabapps/django-email-as-username
* jquery.cookie.js (1.3) - https://github.com/carhartl/jquery-cookie
* kontrolvm-node - https://github.com/jawr/kontrolvm-node

Installation Notes
==================
The following instructions are for Debian systems.

KontrolVM-node
--------------
The kontrolvm-node is run on node systems to perform tasks that can not be done
via libvirt.py it is meant to be run on the openvpn tunnel address.

It should also be noted that kontrolvm-node requires celery and an additional 
process to run the worker. In future a wrapper script will combine these two
in to one file that logs output and wraps them into 1 thread of sorts.

```bash
  git clone https://github.com/jawr/kontrolvm-node.git
  cd kontrolvm-node
  screen -S kontrolvm-node
  ./main.py -p 5000 -l <openvpn_tunnel_addr>
  celery worker -A tasks.installationdisk
```

OpenVPN
-------
The following describes how to setup an OpenVPN server with the ability to add 
client certificates (Nodes).

```bash
  apt-get install openvpn
  cp -r /usr/share/doc/openvpn/examples/easy-rsa/ /etc/openvpn/
  cd /etc/openvpn/easy-rsa/2.0/
  . ./vars
  ./clean-all
  ./build-ca
```

You will be prompted to setup your certificate parameters.

```bash
  ./build-key-server server
  ./build-dh
```
  
Once we have set this up, we can (at any time) generate client keys.

```bash
  ./build-key client1
  ./build-key client2
  ./build-ket clientN
```

Once this is done we need a client and server config file, templates for these
can be found at:

* http://www.kontrolvm.com/openvpn/client.conf
* http://www.kontrolvm.com/openvpn/server.conf

For a client to be able to connect, it needs the following files:

* ca.crt  
* client.conf
* client.crt
* client.key

Make sure that the server has the following files:

* ca.crt
* ca.key
* server.conf
* server.crt
* server.csr
* server.key
* dh1024.pem

Installation Issues
===================
Some common issues you might come across when setting up the system.

Libvirt
-------
Libvirt does not listen on TCP sockets. By default most init scripts set this to
only listen on unix sockets. To fix this open (on Debian) /etc/default/libvirtd
and add "-l" to libvirtd_opts as the comment suggests.
