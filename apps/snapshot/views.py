from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.instance.models import Instance
from apps.snapshot.models import Snapshot
from apps.snapshot.tasks import create_snapshot
import simplejson
import persistent_messages
import libvirt

@login_required
def create(request, name):
  instance = get_object_or_404(Instance, name=name)
  if Snapshot.objects.filter(creating=True, instance=instance).count() > 0:
    persistent_messages.add_message(request, persistent_messages.ERROR, 'Unable to create a snapshot for %s, already creating one.' % (instance))
  else:
    persistent_messages.add_message(request, persistent_messages.INFO, 'Attempting to create a snapshot for %s' % (instance))
    create_snapshot.delay(instance.name) # no need to collect task as it is one blocking method
  return redirect('/instance/%s/' % (name))

@login_required
def delete(request, name, pk):
  instance = get_object_or_404(Instance, name=name)
  snapshot = get_object_or_404(Snapshot, pk=pk)
  
  try:
    dom = instance.get_instance()
    if not dom: raise libvirt.libvirtError()
    snap = snapshot.get_snapshot()
    if snap: snap.delete(0)
    snapshot.delete()
    persistent_messages.add_message(request, persistent_messages.SUCCESS, 'Deleted snapshot for %s' % (instance))
  except libvirt.libvirtError as e:
    persistent_messages.add_message(request, persistent_messages.ERROR, 'Unable to delete snapshot %s for %s: %s' % (snapshot.name, instance, e))
  
  return redirect('/instance/%s/' % (name))
  
@login_required
def edit(request):
  if request.is_ajax() and request.method == 'POST':
    json = request.POST
    try:
      snapshot = Snapshot.objects.get(id=json['pk'])
      if not request.user.is_staff:
        if request.user != snapshot.instance.user: raise Http404
      orig_name = snapshot.name
      orig_value = None
      orig_value = snapshot.name
      snapshot.name = json['value']
      snapshot.save()
      messages.add_message(request, persistent_messages.SUCCESS,
        'Changed Snapshot %s %s from %s to %s' % (orig_name, json['name'], orig_value, json['value']))
    except Snapshot.DoesNotExist:
      raise Http404
    return HttpResponse('{}', mimetype="application/json")
  raise Http404
