from django.utils import unittest
from apps.hypervisor.models import Hypervisor
from apps.shared.models import Size

class HypervisorTestCase(unittest.TestCase):
  def setUp(self):

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
