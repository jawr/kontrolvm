from django.template import RequestContext, loader
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse, Http404
from apps.instance.models import Instance, InstanceTask
from apps.instance.forms import InstanceTaskForm
from apps.installationdisk.forms import InstallationDisksForm
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

  instance.update()

  installationdisks_form = InstallationDisksForm(instance)
  if request.method == 'POST':
    installationdisks_form = InstallationDisksForm(instance, request.POST)
    if installationdisks_form.is_valid():
      instance.attach_disk(installationdisks_form.cleaned_data['installation_disk'], request)

  response = {
    'instance': instance,
    'installationdisks_form': installationdisks_form
  }

  try:
    dom = instance.get_instance()
    if dom:
      tree = ElementTree.fromstring(dom.XMLDesc(0))

      # ensure our volume has it's device name
      if not instance.volume.device_name:
        for dev in tree.findall('devices/disk'):
          path = dev.find('source')
          if path: path = path.get('file')
          else: continue
          if path == instance.volume.path():
            instance.volume.device_name = "/dev/%s" % (dev.find('target').get('dev'))
            instance.volume.save()
            break

  except libvirt.libvirtError as e:
    pass

  return render_to_response('instance/instance.html', response,
    context_instance=RequestContext(request))

@staff_member_required
def edit(request):
  if request.is_ajax() and request.method == 'POST':
    json = request.POST
    try:
      print json['name']
      instance = Instance.objects.get(name=json['pk'])
      orig_name = instance.alias
      orig_value = None
      if json['name'] == 'name':
        orig_value = instance.alias
        instance.alias = json['value']
      else:
        print "no match"
        raise Http404
      instance.save()
      messages.add_message(request, persistent_messages.SUCCESS, 
        'Changed Instance %s %s from %s to %s' % (orig_name, json['name'], orig_value, json['value']))
    except Instance.DoesNotExist:
      print "doesnt exist"
      raise Http404
    return HttpResponse('{}', mimetype="application/json")
  print "other"
  raise Http404

def update(request, name):
  instance = get_object_or_404(Instance, name=name)
  if not request.user.is_staff and request.user != instance.user:
    raise Http404
  instance.update(True)
  return redirect('/instance/' + instance.name + '/')
  

def start(request, name):
  instance = get_object_or_404(Instance, name=name)
  if not request.user.is_staff and request.user != instance.user:
    raise Http404

  dom = instance.get_instance()
  if dom:
    dom.create()
    instance.update(True)
    messages.add_message(request, persistent_messages.INFO,
      'Started instance %s' % (instance))
  else:
    messages.add_message(request, persistent_messages.ERROR,
      'Unable to get instance %s when trying to Start it' % (instance))

  return redirect('/instance/' + instance.name + '/')
     
def resume(request, name):
  instance = get_object_or_404(Instance, name=name)
  if not request.user.is_staff and request.user != instance.user:
    raise Http404

  dom = instance.get_instance()
  if dom:
    dom.resume()
    instance.update(True)
    messages.add_message(request, persistent_messages.INFO,
      'Resumed instance %s' % (instance))
  else:
    messages.add_message(request, persistent_messages.ERROR,
      'Unable to get instance %s when trying to Resume it' % (instance))

  return redirect('/instance/' + instance.name + '/')

def suspend(request, name):
  instance = get_object_or_404(Instance, name=name)
  if not request.user.is_staff and request.user != instance.user:
    raise Http404

  dom = instance.get_instance()
  if dom:
    dom.suspend()
    instance.update(True)
    messages.add_message(request, persistent_messages.INFO,
      'Suspended instance %s' % (instance))
  else:
    messages.add_message(request, persistent_messages.ERROR,
      'Unable to get instance %s when trying to Suspend it' % (instance))

  return redirect('/instance/' + instance.name + '/')

def shutdown(request, name):
  instance = get_object_or_404(Instance, name=name)
  if not request.user.is_staff and request.user != instance.user:
    raise Http404

  dom = instance.get_instance()
  if dom:
    dom.shutdown()
    instance.update(True)
    messages.add_message(request, persistent_messages.INFO,
      'Shutdown instance %s' % (instance))
  else:
    messages.add_message(request, persistent_messages.ERROR,
      'Unable to get instance %s when trying to Shutdown' % (instance))

  return redirect('/instance/' + instance.name + '/')

def force(request, name):
  instance = get_object_or_404(Instance, name=name)
  if not request.user.is_staff and request.user != instance.user:
    raise Http404

  dom = instance.get_instance()
  if dom:
    dom.destroy()
    instance.update(True)
    messages.add_message(request, persistent_messages.INFO,
      'Force Shutdown instance %s' % (instance))
  else:
    messages.add_message(request, persistent_messages.ERROR,
      'Unable to get instance %s when trying to Force Shutdown' % (instance))

  return redirect('/instance/' + instance.name + '/')

def restart(request, name):
  instance = get_object_or_404(Instance, name=name)
  if not request.user.is_staff and request.user != instance.user:
    raise Http404

  dom = instance.get_instance()
  if dom:
    dom.reboot(0)
    instance.update(True)
    messages.add_message(request, persistent_messages.INFO,
      'Restarted instance %s' % (instance))
  else:
    messages.add_message(request, persistent_messages.ERROR,
      'Unable to get instance %s when trying to Restart it' % (instance))

  return redirect('/instance/' + instance.name + '/')

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
def delete(request, name):
  instance = get_object_or_404(Instance, name=name)
  instance.delete(request)
  return redirect('/instance/')

@staff_member_required
def delete_task(request, pk):
  task = get_object_or_404(InstanceTask, pk=pk)
  task.abort(request)
  persistent_messages.add_message(request, persistent_messages.INFO,
    'Delete Instance creating task of %s on %s' % (task.name, task.storagepool.hypervisor), user=task.creator)
  task.delete(request)
  return redirect('/instance/')
