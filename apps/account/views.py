from django.template import RequestContext, loader
from django.shortcuts import redirect, render_to_response
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db.models import Q
import persistent_messages
from emailusernames.utils import get_user
from apps.account.forms import LoginForm
from apps.account.models import UserLogin, InvalidLogin, UserBrowser
from apps.hypervisor.models import Hypervisor
from apps.storagepool.models import StoragePool
from apps.volume.models import Volume
from apps.installationdisk.models import InstallationDisk, InstallationDiskTask
from apps.instance.models import Instance, InstanceTask
from apps.vnc.models import Session
from utils.vnc import VNCSessions

def get_client_ip (request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


@login_required
def index(request):
  unread_messages = persistent_messages.models.Message.objects.filter(user=request.user,
    read=False).order_by('-pk')
  read_messages = persistent_messages.models.Message.objects.filter(user=request.user,
    read=True).order_by('-pk')
  my_instances_online = Instance.objects.filter(status=1, user=request.user)
  my_instances_offline = Instance.objects.filter(~Q(status=1), user=request.user)
  response = {
      'unread_messages': unread_messages,
      'read_messages': read_messages,
      'my_instances_online': my_instances_online,
      'my_instances_offline': my_instances_offline
  }

  if request.user.is_staff:
    hypervisors_online = Hypervisor.objects.filter(status='UP').count()
    hypervisors_offline = Hypervisor.objects.filter(~Q(status='UP')).count()
    storagepools_online = StoragePool.objects.filter(status=2).count()
    storagepools_offline = StoragePool.objects.filter(~Q(status=2)).count()
    volumes_online = Volume.objects.filter(storagepool__status=2).count()
    volumes_offline = Volume.objects.filter(~Q(storagepool__status=2)).count()
    instances_online = Instance.objects.filter(status=1).count()
    instances_offline = Instance.objects.filter(~Q(status=1)).count()
    instancetasks = InstanceTask.objects.all().count()
    installationdisks = InstallationDisk.objects.all().count()
    installationdisktasks = InstallationDiskTask.objects.all().count()
    vnc_sessions = Session.objects.filter(active=True).count()
    vnc_sessions_total = Session.objects.all().count()
    vnc_sessions_rt = VNCSessions().count()

    response['hypervisors_online'] = hypervisors_online
    response['hypervisors_offline'] = hypervisors_offline
    response['storagepools_online'] = storagepools_online
    response['storagepools_offline'] = storagepools_offline
    response['volumes_online'] = volumes_online
    response['volumes_offline'] = volumes_offline
    response['instances_online'] = instances_online
    response['instances_offline'] = instances_offline
    response['instancetasks'] = instancetasks
    response['installationdisks'] = installationdisks
    response['installationdisktasks'] = installationdisktasks
    response['vnc_sessions'] = vnc_sessions
    response['vnc_sessions_rt'] = vnc_sessions_rt
    response['vnc_sessions_total'] = vnc_sessions_total

  return render_to_response('account/index.html', response,
    context_instance=RequestContext(request))
    

def account_login(request):
  if request.user.is_authenticated():
    return redirect('/account/')

  form  = LoginForm()
  error = None

  if request.method == 'POST':
    form = LoginForm(request.POST)
    if form.is_valid():
      username = request.POST['username']
      password = request.POST['password']
      user = authenticate(email=username, password=password)

      (browser, created) = UserBrowser.objects.get_or_create(
        name=request.META['HTTP_USER_AGENT'])
      if created: browser.save()

      if user and user.is_active:
        '''
          Handle Successful login
        '''
        userLogin = UserLogin.objects.create(
          user=user,
          browser=browser,
          address=get_client_ip(request)
        )
        userLogin.save()
        login(request, user)
        # send message
        messages.add_message(request, messages.SUCCESS, 'Logged in')
        return redirect('/account/')

      else:
        userLogin = InvalidLogin.objects.create(
          user=username,
          browser=browser,
          address=get_client_ip(request)
        )
        userLogin.save()
        error = 'Invalid username or password.' 
        
  return render_to_response('account/login.html', {
    'form': form,
    'error': error
  },
  context_instance=RequestContext(request))

@login_required
def account_logout(request):
  logout(request)
  return redirect('/account/') 
