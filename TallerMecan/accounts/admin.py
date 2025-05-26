from django.contrib import admin
from .models import Item, Stock,ServiceType,SoldService,SoldItem

admin.site.register(Item)
admin.site.register(Stock)
admin.site.register(ServiceType)
admin.site.register(SoldService)
admin.site.register(SoldItem)
