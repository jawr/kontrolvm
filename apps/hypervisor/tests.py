from django.test import Client, TestCase
from django.contrib.auth.models import User
from apps.shared.tests import check_url_perms, get_dummy_user, get_dummy_hypervisor

class HypervisorTestCase(TestCase):
  def setUp(self):
    # create a test user
    self.user = get_dummy_user()

    # try localhost and default ports
    self.item = get_dummy_hypervisor()

  """
    Test View permissions
  """
  def test_hypervisor_index_perms(self):
    check_url_perms(self, self.user, '/hypervisor/')

  def test_hypervisor_instance_perms(self):
    check_url_perms(self, self.user, '/hypervisor/1/')

  def test_hypervisor_add_perms(self):
    check_url_perms(self, self.user, '/hypervisor/add/')

  """
    Test Hypervisor model methods
  """

  def test_string_display(self):
    self.assertEqual(str(self.item), 'Test Name [Test Location][Initalize]')

  def test_get_node_address(self):
    self.assertEqual(self.item.get_node_address(), 'http://127.0.0.1:5000')

  def test_get_libvirt_address(self):
    self.assertEqual(self.item.get_libvirt_address(), 'qemu+tcp://127.0.0.1:16509/system')

  def test_get_status_html(self):
    self.assertEqual(self.item.get_status_html(), '<span class="label label-warning">Initalize</span>')

  def test_get_libvirt_status_html(self):
    self.assertEqual(self.item.get_libvirt_status_html(), '<span class="label label-error">Not Responding</span>')

  def test_get_connection(self):
    self.assertEqual(self.item.get_connection(), None)
    """
      could add additional checks here to see that force update works as expected, however, we would
      also need to gurantee that nothing was running localy to connect. i.e.

      ret = self.item.get_connection(True)
      self.assertEqual(ret, None)
      self.assertEqual(self.item.status, 'DN')
    """
