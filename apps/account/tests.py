from django.test import Client, TestCase
from apps.shared.tests import check_url_perms, get_dummy_user
from apps.account.models import UserAudit, UserProfile, UserBrowser, UserLogin, InvalidLogin
from apps.account.forms import LoginForm
from apps.account.views import account_login


class UserAuditTestCase(TestCase):
  def setUp(self):
    self.user = get_dummy_user()
    self.client = Client(HTTP_USER_AGENT='Mozilla/5.0')
    self.client.login(email='test@example.com', password='test-password')
    self.client.get('/')
    self.audit = UserAudit.objects.filter(user=self.user).order_by('-time')[0]

  def test_user_audit(self):
    self.assertEqual(self.audit.page, '/')

  """
    Test UserAudit methods
  """

  def test_current_ip(self):
    self.assertEqual(self.audit.current_ip(), '<error>')

  def test_current_browser(self):
    self.assertEqual(self.audit.current_browser(), '<error>')
    

class UserProfileTestCase(TestCase):
  def setUp(self):
    self.user = get_dummy_user()
    self.client = Client(HTTP_USER_AGENT='Mozilla/5.0')
    self.client.login(email='test@example.com', password='test-password')
    self.client.get('/')
    self.audit = UserAudit.objects.filter(user=self.user).order_by('-time')[0]

  """
    Test UserProfile methods
  """
  def test_string(self):
    self.assertEqual(str(self.user.get_profile()), "%s's Profile" % (self.user.username))

  def test_audit(self):
    self.assertEqual(self.audit, self.user.get_profile().audit())

  def test_instance_count(self):
    self.assertEqual(self.user.get_profile().instance_count(), 0)

  def test_vnc_session_count(self):
    self.assertEqual(self.user.get_profile().vnc_session_count(), 0)
    

class UserBrowserTestCase(TestCase):
  def setUp(self):
    self.user = get_dummy_user()
    self.client = Client(HTTP_USER_AGENT='Mozilla/5.0')
    self.client.login(email='test@example.com', password='test-password')
    self.client.get('/')
    self.browser, created = UserBrowser.objects.get_or_create(name='Mozilla/5.0')

  def test_string(self):
    self.assertEqual(str(self.browser), 'Mozilla/5.0')


"""
  These tests depend on too many variants to test properly
"""
class UserLoginTestCase(TestCase):
  def setUp(self):
    pass

class InvalidLoginTestCase(TestCase):
  def setUp(self):
    pass
