from django.template import RequestContext, loader
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse, Http404
from apps.hypervisor.models import Hypervisor
from apps.installationdisk.models import InstallationDisk, InstallationDiskTask
from apps.installationdisk.forms import InstallationDiskTaskForm
from django.contrib import messages
import persistent_messages
from utils import node
import os

@staff_member_required
def index(request):
  disks = InstallationDisk.objects.all()
  tasks = InstallationDiskTask.objects.all()
  for task in tasks:
    task.get_status()
    if task.state == 'SUCCESS':
      persistent_messages.add_message(request, persistent_messages.SUCCESS, 
        'Successfully downloaded %s on %s.' % (task.name, task.hypervisor),
        user=task.user)
      (disk, created) = InstallationDisk.objects.get_or_create(
        name=task.name,
        hypervisor=task.hypervisor,
        url=task.url,
        filename=task.filename,
        total_bytes=task.total_bytes,
        user=task.user
      )
      if created: disk.save()
      task.delete()
      
  return render_to_response('installationdisk/index.html', {
      'disks': disks,
      'tasks': tasks
    },
    context_instance=RequestContext(request))

@staff_member_required
def edit(request):
  if request.is_ajax() and request.method == 'POST':
    json = request.POST
    try:
      installationdisk = InstallationDisk.objects.get(pk=json['pk'])
      orig_name = installationdisk.name
      orig_value = None
      if json['name'] == 'name':
        orig_value = installationdisk.name
        installationdisk.name = json['value']
      else:
        raise Http404
      installationdisk.save()
      messages.add_message(request, persistent_messages.SUCCESS, 
        'Changed Installation Disk %s %s from %s to %s' % (orig_name, json['name'], orig_value, json['value']))
    except InstallationDisk.DoesNotExist:
      raise Http404
    return HttpResponse('{}', mimetype="application/json")
  raise Http404

@staff_member_required
def add(request):
  form = InstallationDiskTaskForm()
  
  if request.method == "POST":
    conn = form = InstallationDiskTaskForm(request.POST)
    if form.is_valid():
     
      (task, created) = InstallationDiskTask.objects.get_or_create(
        name=form.cleaned_data['name'],
        hypervisor=form.cleaned_data['hypervisor'],
        url=form.cleaned_data['url'],
        filename=form.cleaned_data['url'].split('/')[-1],
        task_id="dummy",
        user=request.user
      )
      if created: task.save()
      task.start()
      messages.add_message(request, persistent_messages.INFO,
        'Attempting to download %s on %s' % (task.filename, task.hypervisor))
      return redirect('/installationdisk/')

  return render_to_response('installationdisk/add.html', {
      'form': form,
    },
    context_instance=RequestContext(request))

@staff_member_required
def delete(request, pk):
  task = get_object_or_404(InstallationDisk, pk=pk)
  task.delete(request)
  return redirect('/installationdisk/')

@staff_member_required
def delete_task(request, pk):
  task = get_object_or_404(InstallationDiskTask, pk=pk)
  task.abort()
  persistent_messages.add_message(request, persistent_messages.INFO,
    'Delete download task of %s on %s' % (task.filename, task.hypervisor), user=task.user)
  task.delete() # might need to do some cleanup here, or check
  # that the task isn't still running
  return redirect('/installationdisk/')


@staff_member_required
def restart(request, pk):
  task = get_object_or_404(InstallationDiskTask, pk=pk)
  task.abort()
  task.start()
  persistent_messages.add_message(request, persistent_messages.INFO,
    'Trying to redownload %s on %s' % (task.filename, task.hypervisor), user=task.user)
  return redirect('/installationdisk/')
