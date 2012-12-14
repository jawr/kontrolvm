from django.template import RequestContext, loader
from django.shortcuts import redirect, render_to_response
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
import persistent_messages
from emailusernames.utils import get_user
from apps.account.forms import LoginForm
from apps.account.models import UserLogin, InvalidLogin, UserBrowser

def get_client_ip (request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


@login_required
def account(request):
  unread_messages = persistent_messages.models.Message.objects.filter(user=request.user,
    read=False)
  read_messages = persistent_messages.models.Message.objects.filter(user=request.user,
    read=True)
  return render_to_response('account/index.html', {
      'unread_messages': unread_messages,
      'read_messages': read_messages,
    },
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
