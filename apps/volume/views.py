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
      (volume, created) = Volume.objects.get_or_create(
        name=form.cleaned_data['name'],
        storagepool=form.cleaned_data['storagepool']
      )
      if created: volume.save()
      return redirect('/volume/')

  return render_to_response('volume/add.html', {
      'form': form,
    },
    context_instance=RequestContext(request))
