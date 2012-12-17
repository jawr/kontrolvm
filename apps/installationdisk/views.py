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
    print task.get_status()
  return render_to_response('installationdisk/index.html', {
      'disks': disks,
      'tasks': tasks
    },
    context_instance=RequestContext(request))

@staff_member_required
def add(request):
  form = InstallationDiskTaskForm()
  
  if request.method == "POST":
    conn = form = InstallationDiskTaskForm(request.POST)
    if form.is_valid():
      hypervisor = form.cleaned_data['hypervisor']
      url = form.cleaned_data['url']
      task_id = node.send_command(hypervisor, 'installationdisk_download', 
      {
        'url': url, 
        'path': hypervisor.install_medium_path
      })
     
      (task, created) = InstallationDiskTask.objects.get_or_create(
        name=form.cleaned_data['name'],
        hypervisor=hypervisor,
        url=url,
        filename=url.split('/')[-1],
        task_id=task_id
      )
      if created: task.save()
      return redirect('/installationdisk/')

  return render_to_response('installationdisk/add.html', {
      'form': form,
    },
    context_instance=RequestContext(request))
