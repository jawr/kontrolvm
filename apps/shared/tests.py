from django.test import Client
from django.contrib.auth.models import User
from apps.hypervisor.models import Hypervisor
from apps.shared.models import Size

def check_url_perms(test, user, url):
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

def get_dummy_user():
  user, created = User.objects.get_or_create(email="test@example.com")
  user.set_password("test-password")
  user.save()
  return user

def get_dummy_size():
  size, created = Size.objects.get_or_create(name="1GB", size=1073741824)
  return size

def get_dummy_hypervisor():
  size = get_dummy_size()
  hypervisor, created = Hypervisor.objects.get_or_create(
    name = 'Test Name',
    location = 'Test Location',
    address = '127.0.0.1',
    install_medium_path = '/tmp',
    maximum_memory = size,
    maximum_hdd = size,
    maximum_vcpus = 1
  )
  return hypervisor

