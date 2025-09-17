from django.contrib import admin
from . import models

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
from .forms import CustomUserCreationForm 


admin.site.register(models.State_details)
admin.site.register(models.StateMusic)
admin.site.register(models.StateFestival)
class StateAdmin(admin.ModelAdmin):
    list_display = ("name", "image")
    search_fields = ("name",) 


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    add_form = CustomUserCreationForm  

    list_display = ['email', 'name', 'is_staff', 'is_active']
    search_fields = ('email', 'name')
    ordering = ('email',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('name', 'avatar', 'bio')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {'fields': ('email', 'name', 'password1', 'password2', 'avatar')}),
    )
admin.site.register(CustomUser,CustomUserAdmin)
