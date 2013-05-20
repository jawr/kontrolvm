from celery import task
from django.http import HttpRequest
from apps.instance.models import Instance
from apps.snapshot.models import Snapshot, SNAPSHOT_TEMPLATE
import persistent_messages
import libvirt
  
@task()
def create_snapshot(instance_name):
  instance = Instance.objects.get(name=instance_name)
  dom = instance.get_instance()
  snapshot = Snapshot(instance=instance)
  snapshot.save()
  if not dom:
    snapshot.status = 'Unable to get Instance (%s) in order to create snapshot' % (instance)

  current_time = snapshot.get_unixtime()

  snapshot_name = "%s_%d" % (instance.name, current_time)
  xml = SNAPSHOT_TEMPLATE % (snapshot_name)
  try:
    dom.snapshotCreateXML(xml, 0)
    snapshot.status = 'Created snapshot for %s' % (instance)
    snapshot.creating = False
    snapshot.save()
  except libvirt.libvirtError as e:
    snapshot.status = 'Unable to create snapshot for %s: %s' % (instance, e)
  snapshot.save()

