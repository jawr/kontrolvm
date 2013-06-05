from django.template import RequestContext, loader
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404
from apps.instance.models import Instance, InstanceTask, InstanceCloneTask
from apps.instance.forms import InstanceTaskForm, InstanceCloneTaskForm
from apps.installationdisk.forms import InstallationDisksForm
from apps.instance.tasks import create_instance, clone_instance
from apps.snapshot.forms import SnapshotForm
from apps.snapshot.tasks import restore_snapshot
from apps.snapshot.models import Snapshot
from apps.storagepool.models import StoragePool
from apps.network.models import InstanceNetwork
from apps.network.forms import NetworkListForm, IPForm
from django.contrib import messages
from xml.etree import ElementTree
from utils import node
import persistent_messages
import simplejson
import libvirt
import time

def instance_init(request, name):
  instance = get_object_or_404(Instance, name=name)

  # check if user is staff or owner
  if not request.user.is_staff and request.user != instance.user:
    raise Http404

  if request.method == 'GET':
    if 'init' in request.GET:
      instance.initialised = True
      instance.save()

  if not instance.initialised:
    instance.update(True)
  else:
    instance.update()

  return instance

@login_required
def instance(request, name):
  return instance_main(request, instance_init(request, name))

@login_required
def instance_form(request, name, form):
  instance = instance_init(request, name)
  if request.method == 'POST':
    if form == 'installation_disk':
      installationdisks_form = InstallationDisksForm(instance, request.POST)
      if installationdisks_form.is_valid():
        instance.attach_disk(installationdisks_form.cleaned_data['installation_disk'], request)

    if form == 'snapshot':
      snapshots_form = SnapshotForm(instance, request.POST)
      if snapshots_form.is_valid():
        restore_snapshot(snapshots_form.cleaned_data['snapshot'], request)

  return instance_main(request, instance)

def instance_main(request, instance):

  # internal cache
  cache = request.session.get(instance.name, False)
  if cache:
    if (time.time() - cache['time']) > 30.0:
      cache = {
        'time': time.time(),
        'cpu_percent': get_cpu_usage(instance),
        'memory_percent': get_memory_usage(instance)[1],
      }
      request.session[instance.name] = cache
      
  else: 
    cache = {
      'time': time.time(),
      'cpu_percent': get_cpu_usage(instance),
      'memory_percent': get_memory_usage(instance)[1],
    }
    request.session[instance.name] = cache

  snapshots = Snapshot.objects.filter(instance=instance)

  installationdisks_form = InstallationDisksForm(instance)
  snapshots_form = None
  if instance.status == 5:
    snapshots_form = SnapshotForm(instance)

  networks = InstanceNetwork.objects.filter(instance=instance)
  hypervisor = instance.volume.storagepool.hypervisor
  for network in networks:
    (rx, tx) = network.get_rx_tx()
    network.rx = rx
    network.tx = tx

  response = {
    'instance': instance,
    'installationdisks_form': installationdisks_form,
    'snapshots_form': snapshots_form,
    'snapshots': snapshots,
    'cpu_percent': request.session[instance.name]['cpu_percent'],
    'memory_percent': request.session[instance.name]['memory_percent'],
    'networks': networks,
  }

  # possibly move this into the instance creation task
  try:
    # ensure our volume has it's device name
    if not instance.volume.device_name:
      dom = instance.get_instance()
      if dom:
        tree = ElementTree.fromstring(dom.XMLDesc(0))
        for dev in tree.findall('devices/disk'):
          path = dev.find('source')
          if path is not None: path = path.get('file')
          else: continue
          if path == instance.volume.path():
            instance.volume.device_name = "/dev/%s" % (dev.find('target').get('dev'))
            instance.volume.save()
            break
  except libvirt.libvirtError as e:
    pass

  return render_to_response('instance/instance.html', response,
    context_instance=RequestContext(request))

# borrowed from https://github.com/retspen/webvirtmgr/blob/master/virtmgr/views.py#L1298

def get_memory_usage(instance):
  hypervisor = instance.volume.storagepool.hypervisor.get_connection()
  dom = instance.get_instance()
  if dom and hypervisor:
    try:
      all_mem = hypervisor.getInfo()[1] * 1048576
      print dom.info()
      dom_mem = dom.info()[1] * 1024
      print dom_mem
      print all_mem
      percent = (dom_mem * 100) / all_mem
      return all_mem, percent
    except libvirt.libvirtError as e:
      pass
    return (0, 0)

def get_cpu_usage(instance):
  hypervisor = instance.volume.storagepool.hypervisor.get_connection()
  dom = instance.get_instance()
  if dom and hypervisor:
    try:
      nbcore = hypervisor.getInfo()[2]
      cpu_use_ago = dom.info()[4]
      time.sleep(1)
      cpu_use_now = dom.info()[4]
      diff_usage = cpu_use_now - cpu_use_ago
      cpu_usage = 100 * diff_usage / (1 * nbcore * 10**9L)
      return cpu_usage
    except libvirt.libvirtError as e:
      pass
  return 0

@login_required
def edit(request):
  if request.is_ajax() and request.method == 'POST':
    json = request.POST
    try:
      instance = Instance.objects.get(name=json['pk'])
      if not request.user.is_staff:
        if request.user != instance.user: raise Http404
      orig_name = instance.alias
      orig_value = None
      if json['name'] == 'name':
        orig_value = instance.alias
        instance.alias = json['value']
      else:
        raise Http404
      instance.save()
      messages.add_message(request, persistent_messages.SUCCESS,
        'Changed Instance %s %s from %s to %s' % (orig_name, json['name'], orig_value, json['value']))
    except Instance.DoesNotExist:
      raise Http404
    return HttpResponse('{}', mimetype="application/json")
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

  if instance.is_base and instance.instance_set.all().count() > 0:
    messages.add_message(request, persistent_messages.ERROR,
      'Unable to start Base Instance %s, too many clones attached to it' % (instance))
    return redirect('/instance/' + instance.name + '/')

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
  instances = Instance.objects.all().order_by('pk')
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
def search(request):
  search = 'Invalid search'
  rows = None
  if request.method == 'POST':
    search_type = int(request.POST.get('search-option'))
    search_text = request.POST.get('search-text')
    search = 'Searching for %s in' % (search_text)

    if search_type == 0:
      rows = Instance.objects.filter(alias__icontains=search_text)
      search += ' Alias'
    elif search_type == 1:
      rows = Instance.objects.filter(name__icontains=search_text)
      search += ' Name'
    elif search_type == 2:
      rows = Instance.objects.filter(user__email__icontains=search_text)
      search += ' User'
    elif search_type == 3:
      rows = Instance.objects.filter(creator__email__icontains=search_text)
      search += ' Creator'
    elif search_type == 4:
      rows = Instance.objects.filter(network__ip__icontains=search_text)
      search += ' IP'

  if search == 'Invalid search':
    rows = Instance.objects.filter()

  return render_to_response('instance/index.html',
    {
    'instances': rows,
    'search': search,
    },
    context_instance=RequestContext(request))

@staff_member_required
def check_resources(request, hypervisor, memory, vcpu, capacity):
  instances = Instance.objects.filter(volume__storagepool__hypervisor=hypervisor)
  allocated_memory = 0
  allocated_vcpus = 0
  allocated_capacity = 0
  for i in StoragePool.objects.filter(hypervisor=hypervisor): 
    allocated_capacity += i.allocated
  for i in instances:
    allocated_memory += i.memory.size
    allocated_vcpus += i.vcpu
  if allocated_memory + memory.size > hypervisor.maximum_memory.size:
    messages.add_message(request, persistent_messages.ERROR,
      'Unable to create instance, <a href="/hypervisor/%d/">Hypervisor</a> has insufficient Memory available to allocate' % (hypervisor.id))
    return False
  elif allocated_vcpus + vcpu > hypervisor.maximum_vcpus:
    messages.add_message(request, persistent_messages.ERROR,
      'Unable to create instance, <a href="/hypervisor/%d/">Hypervisor</a> has insufficient VCPUs available to allocate' % (hypervisor.id))
    return False
  elif allocated_capacity + capacity.size > hypervisor.maximum_hdd.size:
    messages.add_message(request, persistent_messages.ERROR,
      'Unable to create instance, <a href="/hypervisor/%d/">Hypervisor</a> has insufficient Disk space available to allocate' % (hypervisor.id))
    return False
  return True
  
@staff_member_required
def add(request):
  form = InstanceTaskForm()

  if request.method == 'POST':
    form = InstanceTaskForm(request.POST)
    if form.is_valid():
      # first check if we are not overallocating
      hypervisor = form.cleaned_data['storagepool'].hypervisor
      if check_resources(request, hypervisor, form.cleaned_data['memory'], form.cleaned_data['vcpu'], form.cleaned_data['capacity']):
        # end
        name = InstanceTask.get_random_name()
        (instancetask, created) = InstanceTask.objects.get_or_create(
          name=name,
          user=form.cleaned_data['user'],
          creator=request.user,
          vcpu=form.cleaned_data['vcpu'],
          memory=form.cleaned_data['memory'],
          capacity=form.cleaned_data['capacity'],
          storagepool=form.cleaned_data['storagepool'],
          network=form.cleaned_data['network'],
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

# need to decide on permissions for these network based functions
@staff_member_required
def network_delete(request, pk):
  address = get_object_or_404(InstanceNetwork, pk=pk)
  instance = address.instance
  if not request.user.is_staff and request.user != instance.user:
    raise Http404
  instance.detach_network(address)
  return redirect('/instance/%s/' % (instance.name))

@staff_member_required
def network_add(request, name):
  instance = get_object_or_404(Instance, name=name)
  if not request.user.is_staff and request.user != instance.user:
    raise Http404
  form = NetworkListForm()
  ip_form = None
  form['network'].queryset = instance.volume.storagepool.hypervisor.network_set.all()
  if request.method == 'POST':
    form = NetworkListForm(request.POST) # needed in both cases
    if form.is_valid():
      network = form.cleaned_data['network']
      if 'ip_form_add' not in request.POST:
        print "1"
        ip_form = IPForm({'network': network.pk})
        addresses = network.get_available_addresses()
        ip_form.fields['ip'].choices = [(i,i) for i in addresses]
      else:
        ip_form = IPForm(request.POST)
        addresses = form.cleaned_data['network'].get_available_addresses()
        ip_form.fields['ip'].choices = [(i,i) for i in addresses]
        if ip_form.is_valid():
          address = network.create_address_from_ip(ip_form.cleaned_data['ip'])
          print address
          if address:
            address.instance = instance
            address.save()
            instance.attach_network(address)
            return redirect('/instance/%s/' % (instance.name))
  return render_to_response('instance/network_add.html',
    {
      'form': form,
      'ip_form': ip_form,
    },
    context_instance=RequestContext(request))

@staff_member_required
def clone(request, name=None):
  form = InstanceCloneTaskForm()
  if request.method == 'POST':
    form = InstanceCloneTaskForm(request.POST)

  if name:
    instance = get_object_or_404(Instance, name=name)
    form.fields['base'].initial = instance
    form.fields['vcpu'].initial = instance.vcpu
    form.fields['memory'].initial = instance.memory

  if request.method == 'POST' and form.is_valid():
    hypervisor = form.cleaned_data['base'].volume.storagepool.hypervisor
    if check_resources(request, hypervisor, form.cleaned_data['memory'], form.cleaned_data['vcpu'], form.cleaned_data['base'].volume.capacity):
      name = InstanceTask.get_random_name()
      task = InstanceCloneTask.objects.create(
        name=name,
        base=form.cleaned_data['base'],
        user=form.cleaned_data['user'],
        creator=request.user,
        vcpu=form.cleaned_data['vcpu'],
        memory=form.cleaned_data['memory']
      )
      _task = clone_instance.delay(task.pk)
      task.task_id = _task.id
      task.save()
      messages.add_message(request, persistent_messages.INFO,
        'Attempting to Clone Instance: %s' % (task))
  
      return redirect('/instance/')

  return render_to_response('instance/clone.html',
    {
    'form': form,
    },
    context_instance=RequestContext(request))

@staff_member_required
def base(request, name):
  instance = get_object_or_404(Instance, name=name)
  if instance.status != 5:
    messages.add_message(request, persistent_messages.ERROR,
      "Error Instance (%s) must be shutdown to convert into a Base Instance." % (instance))
  else:
    instance.is_base = True
    instance.save()
    messages.add_message(request, persistent_messages.SUCCESS,
      "Instance (%s) marked as a Base Instance." % (instance))
  return redirect('/instance/' + instance.name + '/')
