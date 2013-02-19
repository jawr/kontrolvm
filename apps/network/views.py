from django.template import RequestContext, loader
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse, Http404
from apps.network.models import Network, InstanceNetwork
from apps.network.forms import NetworkForm, InstanceNetworkForm

@staff_member_required
def add(request):
  form = NetworkForm()
  if request.method == 'POST':
    form = NetworkForm(request.POST)
    if form.is_valid():
      form.save()
      return redirect('/network/')

  return render_to_response('network/add.html',
    {
    'form': form,
    },
    context_instance=RequestContext(request))

@staff_member_required
def index(request):
  rows = Network.objects.all()
  return render_to_response('network/index.html',
    {
    'rows': rows,
    },
    context_instance=RequestContext(request))
