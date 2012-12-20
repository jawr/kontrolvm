from django.template import RequestContext, loader
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse, Http404
from apps.instance.models import Instance, InstanceTask
from apps.instance.forms import InstanceTaskForm
from apps.instance.tasks import create_instance
from django.contrib import messages
import persistent_messages
import simplejson

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
