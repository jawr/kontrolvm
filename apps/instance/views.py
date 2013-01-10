from django.template import RequestContext, loader
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse, Http404
from apps.instance.models import Instance, InstanceTask
from apps.instance.forms import InstanceTaskForm
from apps.instance.tasks import create_instance
from django.contrib import messages
from xml.etree import ElementTree
import persistent_messages
import simplejson
import libvirt

def instance(request, name):
  instance = get_object_or_404(Instance, name=name)
  
  # check if user is staff or owner
  if not request.user.is_staff and request.user != instance.user:
    raise Http404

  response = {'instance': instance}

  try:
    dom = instance.get_instance()
    tree = ElementTree.fromstring(dom.XMLDesc(0))

    # ensure our volume has it's device name
    if not instance.volume.device_name:
      for dev in tree.findall('devices/disk'):
        path = dev.find('source').get('file')
        if path == instance.volume.path():
          instance.volume.device_name = "/dev/%s" % (dev.find('target').get('dev'))
          instance.volume.save()
          break

  except libvirt.libvirtError as e:
    pass

  return render_to_response('instance/instance.html', response,
    context_instance=RequestContext(request))

@staff_member_required
def index(request):
  instances = Instance.objects.all()
  tasks = InstanceTask.objects.all()
  for instance in instances:
    instance.update()
  for task in tasks:
    task.update()
  return render_to_response('instance/index.html', {
      'instances': instances,
      'tasks': tasks,
    },
    context_instance=RequestContext(request))

@staff_member_required
def add(request):
  form = InstanceTaskForm()

  if request.method == 'POST':
    form = InstanceTaskForm(request.POST)
    if form.is_valid():
      name = InstanceTask.get_random_name()
      (instancetask, created) = InstanceTask.objects.get_or_create(
        name=name,
        user=form.cleaned_data['user'],
        creator=request.user,
        vcpu=form.cleaned_data['vcpu'],
        memory=form.cleaned_data['memory'],
        disk=form.cleaned_data['disk'],
        storagepool=form.cleaned_data['storagepool']
      )
      if created: instancetask.save()
      task = create_instance.delay(instancetask.name)
      instancetask.task_id = task.id
      instancetask.save()
      messages.add_message(request, persistent_messages.INFO,
        'Attempting to create Instance: %s' % (instancetask))
      return redirect('/instance/')

  return render_to_response('instance/add.html', {
      'form': form,
    },
    context_instance=RequestContext(request))

@staff_member_required
def delete(request, pk):
  task = get_object_or_404(Instance, pk=pk)
  task.delete(request)
  return redirect('/instance/')

@staff_member_required
def delete_task(request, pk):
  task = get_object_or_404(InstanceTask, pk=pk)
  task.abort(request)
  persistent_messages.add_message(request, persistent_messages.INFO,
    'Delete Instance creating task of %s on %s' % (task.name, task.storagepool.hypervisor), user=task.creator)
  task.delete(request)
  return redirect('/instance/')