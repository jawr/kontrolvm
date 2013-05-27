from django.template import RequestContext, loader
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse, Http404
from apps.network.models import Network, InstanceNetwork
from apps.network.forms import NetworkForm, InstanceNetworkForm
from django.contrib import messages
import persistent_messages
import simplejson

@staff_member_required
def add(request):
  form = NetworkForm()
  if request.method == 'POST':
    form = NetworkForm(request.POST)
    print form.errors
    
    if form.is_valid():
      print "is vali"
      form.save()
      return redirect('/network/')

  return render_to_response('network/add.html',
    {
    'form': form,
    },
    context_instance=RequestContext(request))

@staff_member_required
def index(request):
  rows = Network.objects.all()
  for row in rows:
    (rx, tx) = (0,0)
    for i in InstanceNetwork.objects.filter(network=row):
      (_rx,_tx) = i.get_stats()
      rx += _rx
      tx += _tx
    row.rx = rx
    row.tx = tx

  return render_to_response('network/index.html',
    {
    'rows': rows,
    },
    context_instance=RequestContext(request))

@staff_member_required
def edit(request):
  if request.is_ajax() and request.method == 'POST':
    json = request.POST
    try:
      network = Network.objects.get(pk=json['pk'])
      orig = 'default'
      if json['name'] == 'netmask':
        orig = network.netmask
        network.netmask = json['value']
      elif json['name'] == 'gateway':
        orig = network.gateway
        network.gateway = json['value']
      elif json['name'] == 'broadcast':
        orig = network.broadcast
        network.broadcast = json['value']
      elif json['name'] == 'network':
        orig = network.network
        network.network = json['value']
      elif json['name'] == 'start':
        orig = network.start
        network.start = json['value']
      elif json['name'] == 'end':
        orig = network.end
        network.end = json['value']
      else:
        raise Http404
      network.save()
      messages.add_message(request, persistent_messages.SUCCESS, 
        'Changed a Network %s from %s to %s' % (json['name'], orig, json['value']))
    except Network.DoesNotExist:
      raise Http404
    return HttpResponse('{}', mimetype="application/json")
  raise Http404
