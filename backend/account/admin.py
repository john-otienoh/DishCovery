from django.contrib import admin
from .models import User, Profile
# Register your models here.


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = "Profile"


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ["id","email", "name" ,"remember_me", "is_admin"]
    list_filter = ["is_superuser"]
    search_fields = ["email"]
    ordering = ["email" , "id"]
    filter_horizontal = []
    inlines = (ProfileInline,)

admin.site.register(Profile)