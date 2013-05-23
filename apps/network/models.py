from django.db import models
from apps.network.fields import MACAddressField
from apps.hypervisor.models import Hypervisor
from apps.instance.models import Instance

class NoUniqueAddress(Exception): pass

class InstanceNetwork(object): pass

class Network(models.Model):
  hypervisor = models.ForeignKey(Hypervisor)
  device = models.CharField(max_length=20, default='br0')
  netmask = models.GenericIPAddressField()
  gateway = models.GenericIPAddressField()
  broadcast = models.GenericIPAddressField()
  network = models.GenericIPAddressField()
  start = models.GenericIPAddressField()
  end = models.GenericIPAddressField()

  def __unicode__(self):
    return "%s %s - %s :: %s / %s / %s / %s" % (self.hypervisor, self.start, self.end, self.gateway,\
      self.broadcast, self.network, self.netmask)

  def __str__(self):
    return unicode(self).encode('utf-8')

  """
    Warning, does not save address
  """
  def create_unique_address(self):
    start = list(map(int, self.start.split(".")))
    end = list(map(int, self.end.split(".")))
    temp = start
    ranges = []
    ranges.append('%s' % (self.start))
    while temp != end:
      start[3] += 1
      for i in (3, 2, 1):
        if temp[i] == 256:
          temp[i] = 0
          temp[i-1] += 1
      ranges.append(".".join(map(str, temp)))

    addresses = InstanceNetwork.objects.all()
    
    ip = None
    for i in ranges:
      used = False
      for j in addresses:
        if i == j.ip:
          used = True
          break
      if not used:
        ip = i
        break
    if not ip: raise NoUniqueAddress()

    address = InstanceNetwork(ip=ip, network=self)
    return address

  def get_number_of_instances(self):
    return InstanceNetwork.objects.filter(network=self).count()

class InstanceNetwork(models.Model):
  ip = models.GenericIPAddressField(unique=True)
  network = models.ForeignKey(Network)
  instance = models.ForeignKey(Instance)
  mac = MACAddressField(null=True, blank=True)

  def __str__(self):
    return unicode(self).encode('utf-8')

  def __unicode__(self):
    return "%s [%s]" % (self.network, self.ip)
