from django.contrib import admin
from .models import Estado, Cidade

@admin.register(Estado)
class EstadoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'uf')
    search_fields = ('nome', 'uf')

@admin.register(Cidade)
class CidadeAdmin(admin.ModelAdmin):
    list_display = ('nome', 'estado')
    search_fields = ('nome',)
    list_filter = ('estado',)
    list_select_related = ('estado',)