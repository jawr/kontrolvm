from django.template import RequestContext, loader
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse, Http404
from apps.hypervisor.models import Hypervisor
from apps.hypervisor.forms import HypervisorForm
from django.contrib import messages
import persistent_messages
import simplejson

@staff_member_required
def index(request):
  hypervisors = Hypervisor.objects.all()
  return render_to_response('hypervisor/index.html', {
      'hypervisors': hypervisors,
    },
    context_instance=RequestContext(request))

@staff_member_required
def add(request):
  form = HypervisorForm()
  
  if request.method == "POST":
    form = HypervisorForm(request.POST)
    if form.is_valid():
      (hypervisor, created) = Hypervisor.objects.get_or_create(
        name=form.cleaned_data['name'],
        location=form.cleaned_data['location'],
        address=form.cleaned_data['address'],
        timeout=form.cleaned_data['timeout'],
        libvirt_port=form.cleaned_data['libvirt_port'],
        node_port=form.cleaned_data['node_port'],
        install_medium_path=form.cleaned_data['install_medium_path']
      )
      if created: hypervisor.save()
      return redirect('/hypervisor/')

  return render_to_response('hypervisor/add.html', {
      'form': form,
    },
    context_instance=RequestContext(request))

@staff_member_required
def edit(request):
  if request.is_ajax() and request.method == 'POST':
    json = request.POST
    try:
      hypervisor = Hypervisor.objects.get(pk=json['pk'])
      orig_name = hypervisor.name
      orig_value = None
      if json['name'] == 'name':
        orig_value = hypervisor.name
        hypervisor.name = json['value']
      elif json['name'] == 'status':
        orig_value = hypervisor.status
        hypervisor.status = json['value']
      elif json['name'] == 'location':
        orig_value = hypervisor.location
        hypervisor.location = json['value']
      elif json['name'] == 'address':
        orig_value = hypervisor.address
        hypervisor.address = json['value']
      elif json['name'] == 'libvirt_port':
        orig_value = hypervisor.libvirt_port
        hypervisor.libvirt_port = json['value']
      elif json['name'] == 'node_port':
        orig_value = hypervisor.node_port
        hypervisor.node_port = json['value']
      else:
        raise Http404
      hypervisor.save()
      messages.add_message(request, persistent_messages.SUCCESS, 
        'Changed Hypervisor %s %s from %s to %s' % (orig_name, json['name'], orig_value, json['value']))
    except Hypervisor.DoesNotExist:
      raise Http404
    return HttpResponse('{}', mimetype="application/json")
  raise Http404

@staff_member_required
def start(request, pk):
  hypervisor = get_object_or_404(Hypervisor, pk=pk)
  hypervisor.start()
  messages.add_message(request, persistent_messages.SUCCESS,
    'Started Hypervisor %s' % (hypervisor))
  return redirect('/hypervisor/')
  
@staff_member_required
def stop(request, pk):
  hypervisor = get_object_or_404(Hypervisor, pk=pk)
  hypervisor.stop()
  messages.add_message(request, persistent_messages.SUCCESS,
    'Stopped Hypervisor %s' % (hypervisor))
  return redirect('/hypervisor/')

@staff_member_required
def delete(request, pk):
  hypervisor = get_object_or_404(Hypervisor, pk=pk)
  hypervisor.delete()
  return redirect('/hypervisor/')

@staff_member_required
def update(request, pk):
  hypervisor = get_object_or_404(Hypervisor, pk=pk)
  conn = hypervisor.get_connection(True)
  return redirect('/hypervisor/')
