KontrolVM
=========

Kontrol panel is an easy to deploy, easy to manage web application for managing multiple Hypervisors in a variety of locations. It allows users to:

* Attach remote Hypervisors (securely over a VPN)
* Allocate and maintain resource limits (VCPU/Memory/HDD)
* Attach subnets to delegate from, as well as enforcing anti-spoofing rules
* Download installation media (asynchronously) ready for Instance's to mount
* Create, delete and manage Instances
* Create, manage and revert Snapshots
* Attach/Dettach install media available on the Hypervisor
* Provide secure VNC access (over a VPN and only open whilst a HTTP session is also active)
* Monitor Instance's resources

Installation Notes
==================
The following instructions are for Debian systems.

* [KontrolVM](https://github.com/jawr/kontrolvm/wiki/Installation-Debian-Wheezy-7.0.0)
* [Hypervisor setup](https://github.com/jawr/kontrolvm/wiki/Hypervisor-Installation-Debian-Wheezy-7.0.0)

Requirements & Thanks
=====================

* Django - https://www.djangoproject.com/
* libvirt - http://libvirt.org/
* OpenVPN - http://openvpn.net/
* RabbitMQ - http://www.rabbitmq.com/
* Celery (3.0+) - http://www.celeryproject.org
* kontrolvm-node - https://github.com/jawr/kontrolvm-node

Included in requirements.txt (pip install -r requirements.txt):

* psycopg2 - http://initd.org/psycopg/
* requests - http://docs.python-requests.org/en/latest/
* simplejson - https://pypi.python.org/pypi/simplejson/
* django-celery - https://pypi.python.org/pypi/django-celery
* django-dajax - http://www.dajaxproject.com/
* django-dajaxice - http://www.dajaxproject.com/
* django-persistent-messages - https://github.com/philomat/django-persistent-messages
* django-bootstrap-pagination - https://github.com/tgdn/django-bootstrap-pagination
* django-bootstrap-form (2.0.5) - https://github.com/tzangms/django-bootstrap-form
* django-email-as-username (1.6.2) - https://github.com/dabapps/django-email-as-username
* django-bootstrap-pagination () - http://tgdn.github.com/django-bootstrap-pagination/

Included in static:

* Bootstrap (2.2.2) - http://twitter.github.com/bootstrap/
* Flatstrap (0.2) - http://littlesparkvt.com/flatstrap/
* bootbox.js (2.4.2) - http://github.com/makeusabrew/bootbox/
* X-editable () - http://vitalets.github.com/x-editable/
* jquery.cookie.js (1.3) - https://github.com/carhartl/jquery-cookie
* Select2 - http://ivaynberg.github.io/select2/
* Font-Awesome - http://fortawesome.github.io/

License
=======
Copyright (c) 2012 Jess Lawrence

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
