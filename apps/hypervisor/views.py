from django.template import RequestContext, loader
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse, Http404
from apps.hypervisor.models import Hypervisor
from apps.hypervisor.forms import HypervisorForm
import simplejson

@staff_member_required
def index(request):
  hypervisors = Hypervisor.objects.all()
  # iterate over and check status
  #for hypervisor in hypervisors:
  # hypervisor.get_connection()
  return render_to_response('hypervisor/index.html', {
      'hypervisors': hypervisors,
    },
    context_instance=RequestContext(request))

@staff_member_required
def add(request):
  form = HypervisorForm()
  
  if request.method == "POST":
    conn = form = HypervisorForm(request.POST)
    if form.is_valid():
      (hypervisor, created) = Hypervisor.objects.get_or_create(
        name=form.cleaned_data['name'],
        location=form.cleaned_data['location'],
        address=form.cleaned_data['address'],
        timeout=form.cleaned_data['timeout']
      )
      if created: hypervisor.save()
      return redirect('/hypervisor/')

  return render_to_response('hypervisor/add.html', {
      'form': form,
    },
    context_instance=RequestContext(request))

@staff_member_required
def edit(request):
  if request.is_ajax() and request.method == 'POST':
    json = request.POST
    try:
      hypervisor = Hypervisor.objects.get(pk=json['pk'])
      if json['name'] == 'name':
        hypervisor.name = json['value']
      elif json['name'] == 'status':
        hypervisor.status = json['value']
      elif json['name'] == 'location':
        hypervisor.location = json['value']
      elif json['name'] == 'address':
        hypervisor.address = json['value']
      else:
        raise Http404
      hypervisor.save()
    except Hypervisor.DoesNotExist:
      raise Http404
    return HttpResponse("1")
  raise Http404
  

@staff_member_required
def delete(request, pk):
  pass 
