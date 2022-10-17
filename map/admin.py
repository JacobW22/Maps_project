from django.contrib import admin
from map.models import Shop

# Register your models here.

class ShopAdmin(admin.ModelAdmin):
    search_fields = ['name', 'city', 'address' ]

admin.site.register(Shop, ShopAdmin)
