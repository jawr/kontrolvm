from apps.hypervisor.models import Hypervisor
from apps.instance.models import Instance
from apps.storagepool.models import StoragePool
from apps.installationdisk.models import InstallationDisk
from apps.network.models import Network
from apps.account.models import UserProfile, UserAudit
from apps.reversedns.models import ReverseDNSRequest
from datetime import datetime, timedelta
from django.utils import timezone


class KontrolVM(object):

  def process_view(self, request, view_func, view_args, view_kwargs):
    if not request.user.is_authenticated(): return
  
    if UserAudit.objects.filter(user=request.user).count() > 0:
      delta = timedelta(0, 10, 0)
      audit = UserAudit.objects.get(user=request.user)
      if timezone.now() - audit.time > delta:
        audit.page = request.get_full_path()
        audit.save()
    else:
      audit = UserAudit(user=request.user, page=request.get_full_path())
      audit.save()

    if request.user.is_staff:
      request.hypervisor_count = Hypervisor.objects.all().count()
      request.instance_count = Instance.objects.all().count()
      request.storagepool_count = StoragePool.objects.all().count()
      request.installationdisk_count = InstallationDisk.objects.all().count()
      request.network_count = Network.objects.all().count()
      request.user_count = UserProfile.objects.all().count()
      request.rdns_req_count = ReverseDNSRequest.objects.all().count()
