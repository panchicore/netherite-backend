from django.contrib import admin

from vehicles.models import Vehicle, VehicleType, VehicleDocument


class VehicleDocumentInline(admin.StackedInline):
    model = VehicleDocument
    extra = 1


class VehicleAdmin(admin.ModelAdmin):
    list_display = ['id', 'company', 'owner', 'type', 'plate', 'created_at']
    list_filter = ['company']
    inlines = [VehicleDocumentInline]


admin.site.register(Vehicle, VehicleAdmin)
admin.site.register(VehicleType)
admin.site.register(VehicleDocument)
