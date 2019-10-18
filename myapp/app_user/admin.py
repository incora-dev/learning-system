from django.contrib import admin
from myapp.app_user.models import User
from django.contrib.auth.admin import UserAdmin, Group


class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        ('Permissions', {'fields': ('user_type',  'is_superuser')}),
        ('Expand page type', {'fields': ('expand_type',)}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'user_type', 'password1', 'password2', 'is_superuser')}
         ),
    )

    list_filter = ('user_type', 'is_superuser')


admin.site.register(User, CustomUserAdmin)
admin.site.unregister(Group)
