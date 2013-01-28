from dajax.core import Dajax
from dajaxice.decorators import dajaxice_register
from django.conf import settings
from django.contrib import messages
from django.shortcuts import get_object_or_404
from apps.instance.models import Instance
from apps.vnc.models import Session
from utils.vnc import Proxy
import persistent_messages

vnc_sessions = {}

@dajaxice_register
def heartbeat(request, port, name, method):
  try:
    session = Session.objects.get(port=port, active=True)
    instance = Instance.objects.get(name=name)
  except (Session.DoesNotExist, Instance.DoesNotExist):
    # we should perhaps wait for a .join here to ensure
    if port in vnc_sessions: vnc_sessions[port].stop()
  instance.save()

@dajaxice_register
def setup_vnc(request, name):
  instance = get_object_or_404(Instance, name=name)
  if not request.user.is_staff and request.user != instance.user:
    raise Http404

  dajax = Dajax()
  local_port = Session.get_random_port()
  remote_port = instance.get_vnc_port()

  print "Remote port: %d" % (remote_port)
  print "Local port: %d" % (local_port)

  if local_port > 0:
    session = Session(
      user=request.user,
      instance=instance,
      port=local_port
    )
    session.save()

    proxy = Proxy('jess.lawrence.pm', local_port, instance.volume.storagepool.hypervisor.address, remote_port).start()
    vnc_sessions[session.id] = proxy

    html = """
    <applet archive="%sjava/tightvnc-jviewer.jar" code="com.glavsoft.viewer.Viewer" height="460" width="100%%">
        <param name="Show controls" value="Yes">
        <param name="Offer relogin" value="Yes">
        <param name="Open new window" value="No">
        <param name="Scaling factor" value="auto">
        <param name="HOST" value="jess.lawrence.pm">
        <param name="PORT" value="%d">
        <param name="OpenNewWindow" value="no" />
        <param name="ShowControls" value="yes" />
        <param name="ViewOnly" value="no" />
        <param name="AllowClipboardTransfer" value="yes" />
        <param name="RemoteCharset" value="standard" />
        <param name="ScalingFactor" value="80" />
    </applet>""" % (settings.STATIC_URL, local_port)
    dajax.assign('#vnc-applet', 'innerHTML', html)
    dajax.assign('#vnc-connect-button', 'innerHTML', '<i class="icon-off"></i> Disconnect')
    dajax.script('$("#vnc-container").show(2000);')
    dajax.script('connected = 1;');
    dajax.script('session_id = ' + str(session.id) + ';');
    dajax.script('vnc_heartbeat(%d);' % (local_port));
    dajax.script('$("#vnc-connect-button").toggleClass("active")') 
  else:
    dajax.script('$("#vnc-connect-button").toggleClass("active")') 
    dajax.assign('#vnc-connect-button', 'innerHTML', '<i class="icon-share"></i> Retry')
    dajax.assign('#vnc-container-p', 'innerHTML', 'Unable to start VNC Session, unable to get local port')
    dajax.script('$("#vnc-container").show(2000);')

  return dajax.json()
