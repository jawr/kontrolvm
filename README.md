kontrolvm
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

Installation Issues
===================
Some common issues you might come across when setting up the system.

Libvirt
-------
Libvirt does not listen on TCP sockets. By default most init scripts set this to
only listen on unix sockets. To fix this open (on Debian) /etc/default/libvirtd
and add "-l" to libvirtd_opts as the comment suggests.
