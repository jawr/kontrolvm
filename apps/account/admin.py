from django.contrib import admin
from apps.account.models import UserProfile, UserBrowser, UserLogin, InvalidLogin, UserAudit

admin.site.register(UserProfile)
admin.site.register(UserBrowser)
admin.site.register(UserLogin)
admin.site.register(InvalidLogin)
admin.site.register(UserAudit)
