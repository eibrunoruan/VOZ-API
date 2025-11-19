from django.contrib import admin
from .models import OfficialEntity, OfficialResponse

@admin.register(OfficialEntity)
class OfficialEntityAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cidade', 'estado')
    search_fields = ('nome', 'cidade__nome', 'estado__nome')
    list_filter = ('estado',)
    filter_horizontal = ('gestores',)
    list_select_related = ('cidade', 'estado')

@admin.register(OfficialResponse)
class OfficialResponseAdmin(admin.ModelAdmin):
    list_display = ('denuncia', 'entidade', 'data_resposta')
    search_fields = ('denuncia__titulo', 'entidade__nome')
    list_filter = ('entidade',)
    readonly_fields = ('data_resposta',)
    list_select_related = ('denuncia', 'entidade')