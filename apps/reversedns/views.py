from django.template import RequestContext, loader
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404
from apps.reversedns.models import ReverseDNS, ReverseDNSRequest

@staff_member_required
def approve(request, pk):
  pass

@login_required
def request(request):
  pass

@staff_member_required
def index(request):
  approved = ReverseDNS.objects.filter(deleted__isnull=True)
  requests = ReverseDNSRequest.objects.all()

  return render_to_response('reversedns/index.html',
    {
      'approved': approved,
      'requests': requests,
    },
    context_instance=RequestContext(request))
