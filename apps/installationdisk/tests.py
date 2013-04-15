from django.test import TestCase, Client
from apps.shared.tests import check_url_perms, get_dummy_user, get_dummy_hypervisor

class InstallationDiskTestCase(TestCase):
  def setUp(self):
    self.user = get_dummy_user()
    self.item = get_dummy_installationdisk()

  def test_string(self):
    self.assertEqual(str(self.item), "Test Disk")
