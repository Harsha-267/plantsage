from django.contrib import admin
from .models import Plant

# Register your models here.
@admin.register(Plant)
class PlantAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_watering_frequency_display')
    readonly_fields = ('get_watering_frequency_display',)