from django.template import RequestContext, loader
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse, Http404
from apps.volume.models import Volume
from apps.volume.forms import VolumeForm
from django.contrib import messages
import persistent_messages
import simplejson

@staff_member_required
def index(request):
  volumes = Volume.objects.all()
  for volume in volumes:
    volume.update()
  return render_to_response('volume/index.html', {
      'volumes': volumes,
    },
    context_instance=RequestContext(request))

@staff_member_required
def add(request):
  form = VolumeForm()

  if request.method == "POST":
    form = VolumeForm(request.POST)
    if form.is_valid():
      # let's check that we can connect to storage pool
      storagepool = form.cleaned_data['storagepool']
      if not storagepool.get_storagepool():
        messages.add_message(request, persistent_messages.ERROR, 'Unable to connect to Storage Pool %s to create Volume' % (storagepool))
      else:
        name = Volume.create_random_name()
        (volume, created) = Volume.objects.get_or_create(
          name=name,
          storagepool=storagepool,
          capacity=form.cleaned_data['capacity']
        )
        if created: volume.save()
        if not volume.create(request): volume.delete()
        return redirect('/volume/')

  return render_to_response('volume/add.html', {
      'form': form,
    },
    context_instance=RequestContext(request))

@staff_member_required
def delete(request, pk):
  volume = get_object_or_404(Volume, pk=pk)
  volume.delete(request)
  return redirect('/volume/')
