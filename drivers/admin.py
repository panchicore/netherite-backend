from django.contrib import admin

from drivers.models import Driver, DriverDocument


class DriverDocumentInline(admin.TabularInline):
    model = DriverDocument


class DriverAdmin(admin.ModelAdmin):
    inlines = [DriverDocumentInline]
    list_display = ['id', 'company', 'first_name', 'last_name', 'identification', 'user']
    list_filter = ['company']


class DriverDocumentAdmin(admin.ModelAdmin):
    list_display = ['id', 'company', 'driver', 'type']
    list_filter = ['company']


admin.site.register(Driver, DriverAdmin)
admin.site.register(DriverDocument, DriverDocumentAdmin)
