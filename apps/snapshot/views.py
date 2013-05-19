from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404
from apps.instance.models import Instance
from apps.snapshot.models import Snapshot, SNAPSHOT_TEMPLATE
from django.contrib import messages
from xml.etree import ElementTree
import persistent_messages
import simplejson
import libvirt
import time

def create(request, name):
  instance = get_object_or_404(Instance, name=name)
  dom = instance.get_instance()
  if not dom:
    persistent_messages.add_message(request, persistent_messages.ERROR, 'Unable to get Instance (%s) in order to create snapshot' % (instance))

  current_time = time.time()
  snapshot_name = "%s_%d" % (name, current_time)
  xml = SNAPSHOT_TEMPLATE % (snapshot_name, current_time)
  try:
    dom.snapshotCreateXML(xml, 0)
    snapshot = Snapshot(instance=instance)
    snapshot.save()
    persistent_messages.add_message(request, persistent_messages.SUCCESS, 'Created snapshot for %s' % (instance))
  except libvirt.libvirtError as e:
    persistent_messages.add_message(request, persistent_messages.ERROR, 'Unable to create snapshot for %s: %s' % (instance, e))
  return redirect('/instance/%s/' % (name))
