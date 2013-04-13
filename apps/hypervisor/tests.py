from django.utils import unittest
from django.test import Client
from django.contrib.auth.models import User
from apps.hypervisor.models import Hypervisor
from apps.shared.models import Size

def check_url(test, user, url):
  client = Client()
  response = client.get(url, follow=False)
  test.assertEqual(404, response.status_code)
  client.login(email="test@example.com", password="test-password")
  response = client.get(url, follow=False)
  test.assertEqual(404, response.status_code)
  # upgrade user
  user.is_staff = True
  user.save()
  response = client.get(url, follow=False)
  test.assertEqual(200, response.status_code)
  # downgrade user
  user.is_staff = False
  user.save()

class HypervisorTestCase(unittest.TestCase):
  def setUp(self):
    # create a test user
    self.user, created = User.objects.get_or_create(email="test@example.com")
    self.user.set_password("test-password")
    self.user.save()

    # create a test size and test it
    size, created = Size.objects.get_or_create(name="1GB", size=1073741824)
    self.assertEqual(size.name, "1GB")
    self.assertEqual(size.size, 1073741824)

    # try localhost and default ports
    self.item = Hypervisor(
        name = 'Test Name',
        location = 'Test Location',
        address = '127.0.0.1',
        install_medium_path = '/tmp',
        maximum_memory = size,
        maximum_hdd = size,
        maximum_vcpus = 1
    )
    self.item.save()

  """
    Test View permissions
  """
  def test_hypervisor_index_perms(self):
    check_url(self, self.user, '/hypervisor/')

  def test_hypervisor_instance_perms(self):
    check_url(self, self.user, '/hypervisor/1/')

  def test_hypervisor_add_perms(self):
    check_url(self, self.user, '/hypervisor/add/')


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
