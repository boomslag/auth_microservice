from django.contrib import admin

from . import models

# Register your models here.
@admin.register(models.UserAccount)
class PostAdmin(admin.ModelAdmin):
    list_display = ('username','first_name', 'last_name','email', 'is_staff', 'become_seller', 'role','verified')
    list_display_links = ('username','first_name', 'last_name','email', )
    list_filter = ('username','first_name', 'last_name','email', 'is_staff', 'become_seller', 'role',)
    search_fields = ('id','username','first_name', 'last_name','email','role','verified', 'become_seller', )
    list_editable = ('become_seller', 'role', 'verified','is_staff' )
    list_per_page = 25

