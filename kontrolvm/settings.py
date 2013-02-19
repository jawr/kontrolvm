# Django settings for kontrolvm project.
try:
    from local_settings import *
except:
    pass

import djcelery
djcelery.setup_loader()


DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
  ('Jess Lawrence', 'jess@lawrence.pm'),
)

MANAGERS = ADMINS

DATABASES = {
  'default': {
    'ENGINE': 'django.db.backends.sqlite3',
    'NAME': 'db/kontrolvm.db',
    'USER': '',            # Not used with sqlite3.
    'PASSWORD': '',          # Not used with sqlite3.
    'HOST': '',            # Set to empty string for localhost. Not used with sqlite3.
    'PORT': '',            # Set to empty string for default. Not used with sqlite3.
  }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'Europe/London'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-gb'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: '/home/media/media.lawrence.com/media/'
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: 'http://media.lawrence.com/media/', 'http://example.com/media/'
MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' 'static/' subdirectories and in STATICFILES_DIRS.
# Example: '/home/media/media.lawrence.com/static/'

# URL prefix for static files.
# Example: 'http://media.lawrence.com/static/'
STATIC_URL = '/static/'


# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
  'django.contrib.staticfiles.finders.FileSystemFinder',
  'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#  'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

SECRET_KEY = 'ko4k4lkmregeEKLRGKFDMelmfksgng4539tw0gjedfm/G'
# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
  'django.template.loaders.filesystem.Loader',
  'django.template.loaders.app_directories.Loader',
  'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
  'django.middleware.common.CommonMiddleware',
  'django.contrib.sessions.middleware.SessionMiddleware',
  'django.middleware.csrf.CsrfViewMiddleware',
  'django.contrib.auth.middleware.AuthenticationMiddleware',
  'django.contrib.messages.middleware.MessageMiddleware',
  'django.middleware.clickjacking.XFrameOptionsMiddleware',
  'apps.account.middleware.AjaxMessaging',
  'bootstrap_pagination.middleware.PaginationMiddleware',
)

ROOT_URLCONF = 'kontrolvm.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'kontrolvm.wsgi.application'

INSTALLED_APPS = (
  'django.contrib.auth',
  'django.contrib.contenttypes',
  'django.contrib.sessions',
  'django.contrib.sites',
  'django.contrib.messages',
  'django.contrib.staticfiles',
  'django.contrib.admin',
  # libs
  'djcelery',
  'emailusernames',
  'bootstrapform',
  'persistent_messages',
  'dajax',
  'dajaxice',
  'bootstrap_pagination',
  # apps
  'apps.account',
  'apps.hypervisor',
  'apps.storagepool',
  'apps.installationdisk',
  'apps.volume',
  'apps.instance',
  'apps.vnc'
)

AUTHENTICATION_BACKENDS = (
  'emailusernames.backends.EmailAuthBackend',
)

AUTH_PROFILE_MODULE = 'apps.account.UserProfile'

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
  'version': 1,
  'disable_existing_loggers': False,
  'formatters': {
    'verbose': {
      'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
     },
    'simple': {
      'format': '%(levelname)s %(message)s'
    },
  },
  'filters': {
    'require_debug_false': {
      '()': 'django.utils.log.RequireDebugFalse'
    }
  },
  'handlers': {
    'mail_admins': {
      'level': 'ERROR',
      'filters': ['require_debug_false'],
      'class': 'django.utils.log.AdminEmailHandler'
    },
    'console': {
      'level':'DEBUG',
      'class':'logging.StreamHandler',
      'formatter': 'simple'
    },
  },
  'loggers': {
    'django.request': {
      'handlers': ['mail_admins'],
      'level': 'ERROR',
      'propagate': True,
    },
    'dajaxice': {
      'handlers': ['console'],
      'level': 'INFO',
      'propagate': True,
    },
  }
}

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.contrib.auth.context_processors.auth',
    'django.contrib.messages.context_processors.messages',
    'django.core.context_processors.request',
)

LOGIN_REDIRECT_URL = '/account/login/'
LOGIN_URL = '/account/login/'
LOGOUT_URL = '/account/logout'

MESSAGE_STORAGE = 'persistent_messages.storage.PersistentMessageStorage'

DAJAXICE_MEDIA_PREFIX = 'djx'

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'dajaxice.finders.DajaxiceFinder',
)
