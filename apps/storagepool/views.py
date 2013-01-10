from django.template import RequestContext, loader
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse, Http404
from apps.storagepool.models import StoragePool
from apps.storagepool.forms import StoragePoolForm
from apps.hypervisor.models import Hypervisor
from django.contrib import messages
import persistent_messages
import simplejson
import libvirt

@staff_member_required
def index(request):
  storagepools = StoragePool.objects.all()

  for pool in storagepools:
    pool.update()

  return render_to_response('storagepool/index.html', {
      'storagepools': storagepools,
    },
    context_instance=RequestContext(request))

@staff_member_required
def add(request):
  form = StoragePoolForm()
  
  if request.method == "POST":
    conn = form = StoragePoolForm(request.POST)
    if form.is_valid():
      # first we need to create the pool on the hypervisor
      hypervisor = form.cleaned_data['hypervisor']
      conn = hypervisor.get_connection()
      if not conn:
        messages.add_message(request, persistent_messages.ERROR, 
          'Unable to connect to %s Hypervisor. Halting.' % (hypervisor))
      else:
        xml = """
          <pool type="dir">
            <name>%s</name>
            <target><path>%s</path></target>
          </pool>
          """ % (form.cleaned_data['name'], form.cleaned_data['path'])
        try:
          pool = conn.storagePoolDefineXML(xml, 0)
          pool.create(0)
          pool.setAutostart(1)
          
          # create database instance
          (storagepool, created) = StoragePool.objects.get_or_create(
            name=form.cleaned_data['name'],
            hypervisor=form.cleaned_data['hypervisor'],
            path=form.cleaned_data['path'],
          )
          if created: storagepool.save()

          messages.add_message(request, persistent_messages.SUCCESS,
            'Created Storage Pool: %s' % (storagepool))
        
          # return to index
          return redirect('/storagepool/')
        except libvirt.libvirtError as e:
          messages.add_message(request, persistent_messages.ERROR,
            'Unable to create Storage Pool (Check permissions): %s' % (e))

  return render_to_response('storagepool/add.html', {
      'form': form,
    },
    context_instance=RequestContext(request))

@staff_member_required
def edit(request):
  if request.is_ajax() and request.method == 'POST':
    json = request.POST
    try:
      storagepool = StoragePool.objects.get(pk=json['pk'])
      orig_name = storagepool.name
      orig_value = None
      if json['name'] == 'name':
        orig_value = storagepool.name
        storagepool.name = json['value']
      elif json['name'] == 'path':
        orig_value = storagepool.path
        storagepool.path = json['value']
      else:
        raise Http404
      storagepool.save()
      messages.add_message(request, persistent_messages.SUCCESS, 
        'Changed Storage Pool %s %s from %s to %s' % (orig_name, json['name'], orig_value, json['value']))
    except StoragePool.DoesNotExist:
      raise Http404
    return HttpResponse('{}', mimetype="application/json")
  raise Http404

@staff_member_required
def delete(request, pk):
  pool = get_object_or_404(StoragePool, pk=pk)
  pool.delete(request)
  return redirect('/storagepool/')

@staff_member_required
def update(request, pk):
  return redirect('/storagepool/')

@staff_member_required
def start(request, pk):
  pool = get_object_or_404(StoragePool, pk=pk)
  storagepool = pool.get_storagepool()
  if not storagepool:
    messages.add_message(request, persistent_messages.ERROR,
      'Unable to get %s Storage Pool' % (pool.name))
  else:
    try:
      storagepool.create(0)
      messages.add_message(request, persistent_messages.SUCCESS, 
        'Started %s Storage Pool' % (pool.name))
    except libvirt.libvirtError as e:
      messages.add_message(request, persistent_messages.ERROR,
        'Unable to start %s Storage Pool: %s' % (pool.name, e))
  return redirect('/storagepool/')

@staff_member_required
def stop(request, pk):
  pool = get_object_or_404(StoragePool, pk=pk)
  storagepool = pool.get_storagepool()
  if not storagepool:
    messages.add_message(request, persistent_messages.ERROR,
      'Unable to get %s Storage Pool' % (pool.name))
  else:
    try:
      storagepool.destroy()
      messages.add_message(request, persistent_messages.SUCCESS, 
        'Shutdown %s Storage Pool' % (pool.name))
    except libvirt.libvirtError as e:
      messages.add_message(request, persistent_messages.ERROR,
        'Unable to shutdown % Storage Pool: %s' % (pool.name, e))
  return redirect('/storagepool/')
