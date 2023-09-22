# -*- encoding: utf-8 -*-
"""
CyberHackAdemy 2021
"""

from django.contrib.auth.models import User, Group
from django.contrib import admin
from django.db import models
from .models import User, WebSSH
from .models import Lab
from .models import CyberKillChain
from .models import Tag_Args
from .models import Tag_Level
from .models import CTFd_configs
from .models import Notifica, Notifica_vista, Statistiche
from .models import SSHTunnel_configs, MacchinaAttacco
from .models import Settings_Server

# Register your models here.
admin.site.register(User)
admin.site.register(Lab)
# admin.site.register(CyberKillChain)
admin.site.register(Tag_Args)
admin.site.register(Tag_Level)
# admin.site.register(CTFd_configs)
admin.site.register(SSHTunnel_configs)
admin.site.register(Notifica)
admin.site.register(Statistiche)
# admin.site.register(MacchinaAttacco)

# per avere una sola configurazione
@admin.register(CTFd_configs)
class CTFd_configsModelAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        if self.model.objects.count() >= 1:
            return False
        return super().has_add_permission(request)


@admin.register(CyberKillChain)
class CyberKillCHainModelAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        if self.model.objects.count() >= 1:
            return False
        return super().has_add_permission(request)

@admin.register(MacchinaAttacco)
class MacchinaAttaccoModelAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        if self.model.objects.count() >= 1:
            return False
        return super().has_add_permission(request)

@admin.register(WebSSH)
class WebSSHModelAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        if self.model.objects.count() >= 1:
            return False
        return super().has_add_permission(request)

@admin.register(Settings_Server)
class Settings_ServerModelAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        if self.model.objects.count() >= 1:
            return False
        return super().has_add_permission(request)
