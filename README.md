KontrolVM
=========

Kontrol panel for KVM - http://www.kontrolvm.com

Requirements
============

* RabbitMQ - http://www.rabbitmq.com/
* Celery (3.0+) - http://www.celeryproject.org
* Bootstrap (2.2.2) - http://twitter.github.com/bootstrap/
* Flatstrap (0.2) - http://littlesparkvt.com/flatstrap/
* bootbox.js (2.4.2) - http://github.com/makeusabrew/bootbox/
* X-editable () - http://vitalets.github.com/x-editable/
* django-bootstrap-form (2.0.5) - https://github.com/tzangms/django-bootstrap-form
* django-email-as-username (1.6.2) - https://github.com/dabapps/django-email-as-username
* django-bootstrap-pagination () - http://tgdn.github.com/django-bootstrap-pagination/
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
in to one file that logs output and wraps them into one thread of sorts.

```bash
  git clone https://github.com/jawr/kontrolvm-node.git
  cd kontrolvm-node
  screen -S kontrolvm-node
  ./main.py -p 5000 -l <openvpn_tunnel_addr> &
  celery worker -A tasks.installationdisk
```

Bridged Networking
------------------
KontrolVM is designed to provide each instance with it's own public IP address
it achieves this by allowing the guests to use the host's physical interface.

Debian provides a very informative and clear explanation as well as instructions
on setting this up: http://wiki.debian.org/BridgeNetworkConnections

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
  source ./vars
  ./build-key-server server
  ./build-dh
```
  
Once we have set this up, we can (at any time) generate client keys.

```bash
  source ./vars
  ./build-key client1
  ./build-key client2
  ./build-ket clientN
```

Once this is done we need a client and server config file, templates for these
can be found at:

* http://www.kontrolvm.com/openvpn/client.conf
* http://www.kontrolvm.com/openvpn/server.conf

The only change that needs to be changed is the <SERVER_IP> dirivative in both files.

For a client to be able to connect, it needs the following files:

* ca.crt  
* client.conf
* client[N].crt
* client[N].key

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

License
=======
Copyright (c) 2012 Jess Lawrence

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


