from django.template import RequestContext, loader
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404
from apps.reversedns.models import ReverseDNS, ReverseDNSRequest
from apps.reversedns.forms import ReverseDNSRequestForm
from apps.instance.models import Instance
from apps.network.models import InstanceNetwork
from datetime import datetime

@staff_member_required
def approve(request, id):
  rdns_request = get_object_or_404(ReverseDNSRequest, id=id)
 
  if ReverseDNS.objects.filter(net=rdns_request.net).count() > 0:
    ReverseDNS.objects.get(net=rdns_request.net).deleted = datetime.now()
 
  rdns = ReverseDNS(
    net=rdns_request.net,
    instance=rdns_request.instance,
    rdns=rdns_request.rdns,
    approved_by=request.user
  )
  rdns.save()

  rdns_request.delete()
  
  return redirect('/reversedns/approved/')

@login_required
def request(request, id, name):
  instance = get_object_or_404(Instance, name=name)
  network = get_object_or_404(InstanceNetwork, id=id)

  if instance.user != request.user or not request.user.is_staff:
    raise Http404

  if ReverseDNSRequest.objects.filter(net=network).count() > 0:
    raise Http404

  form = ReverseDNSRequestForm()

  if request.method == 'POST':
    form = ReverseDNSRequestForm(request.POST)
    if form.is_valid():
      rdns_request = ReverseDNSRequest(
        net=network,
        instance=instance,
        rdns=form.cleaned_data['rdns'],
        requestor=request.user,
      )
      rdns_request.save()
      return redirect('/instance/%s/#networks/' % (instance.name))

  return render_to_response('reversedns/request.html',
    {
      'form': form,
    },
    context_instance=RequestContext(request))
@staff_member_required
def requests(request):
  rows = ReverseDNSRequest.objects.all()
  return render_to_response('reversedns/requests.html',
    {
      'rows': rows,
    },
    context_instance=RequestContext(request))

@staff_member_required
def approved(request):
  rows = ReverseDNS.objects.filter(deleted__isnull=True)
  return render_to_response('reversedns/approved.html',
    {
      'rows': rows,
    },
    context_instance=RequestContext(request))
