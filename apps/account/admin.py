from django.contrib import admin
from apps.account.models import UserProfile, UserBrowser, UserLogin, InvalidLogin

admin.site.register(UserProfile)
admin.site.register(UserBrowser)
admin.site.register(UserLogin)
admin.site.register(InvalidLogin)
