from django.contrib import admin
from .models import User, Address
from oauth.models import OauthQQUser
from areas.models import Area

admin.site.register(User)
admin.site.register(OauthQQUser)
admin.site.register(Area)
admin.site.register(Address)