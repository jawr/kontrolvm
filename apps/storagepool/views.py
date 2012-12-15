from django.template import RequestContext, loader
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse, Http404
from apps.storagepool.models import StoragePool
from apps.storagepool.forms import StoragePoolForm
from django.contrib import messages
import persistent_messages
import simplejson

@staff_member_required
def index(request):
  storagepools = StoragePool.objects.all()
  for pool in storagepools:
    storagepool = pool.get_storagepool()
    if storagepool:
      (pool.state, capacity, alloc, avail) = storagepool.info()
      pool.save()
      pool.capacity = '%.2f GB' % (capacity/1024/1024/1024.0)
      pool.alloc = '%.2f GB' % (alloc/1024/1024/1024.0)
      pool.avail = '%.2f GB' % (avail/1024/1024/1024.0)
      pool.perc = ((float(alloc)/float(capacity))*100)
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
      (storagepool, created) = StoragePool.objects.get_or_create(
        name=form.cleaned_data['name'],
        hypervisor=form.cleaned_data['hypervisor'],
        path=form.cleaned_data['path'],
      )
      if created: storagepool.save()
      return redirect('/storagepool/')

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
  storagepool = get_object_or_404(StoragePool, pk=pk)
  storagepool.delete()
  return redirect('/storagepool/')

@staff_member_required
def update(request, pk):
  return redirect('/storagepool/')
